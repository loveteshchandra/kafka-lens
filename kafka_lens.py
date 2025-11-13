#!/usr/bin/env python3
"""
Kafka Lens - A CLI tool for Kafka cluster management and monitoring.

This tool provides administrators with simple commands to:
- Check cluster health and identify issues
- Monitor consumer group lag
- Find and clean up stale resources
"""

import os
import sys
import yaml
import boto3
import click
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from kafka.admin import KafkaAdminClient
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform colored output
colorama.init()

class KafkaLens:
    """Main class for Kafka cluster management operations."""
    
    def __init__(self, config_path: str = "config.yml"):
        """Initialize the commander with configuration."""
        self.config = self._load_config(config_path)
        self.admin_client = None
        self.consumer = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            click.echo(f"{Fore.RED}Error: Configuration file '{config_path}' not found.{Style.RESET_ALL}")
            sys.exit(1)
        except yaml.YAMLError as e:
            click.echo(f"{Fore.RED}Error parsing configuration file: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _get_bootstrap_servers(self) -> List[str]:
        """Get bootstrap servers from cloud cluster or static configuration."""
        if 'cluster_arn' in self.config or 'msk_cluster_arn' in self.config:
            return self._get_cloud_bootstrap_servers()
        else:
            servers = self.config.get('bootstrap_servers', 'localhost:9092')
            return servers.split(',') if isinstance(servers, str) else servers
    
    def _get_cloud_bootstrap_servers(self) -> List[str]:
        """Get bootstrap servers from cloud-managed Kafka cluster."""
        try:
            # Support both cluster_arn and msk_cluster_arn for backward compatibility
            cluster_arn = self.config.get('cluster_arn') or self.config.get('msk_cluster_arn')
            if not cluster_arn:
                raise ValueError("cluster_arn or msk_cluster_arn must be specified for cloud clusters")
            
            region = self.config.get('aws_region', 'us-west-2')
            profile = self.config.get('aws_profile')
            
            session = boto3.Session(profile_name=profile) if profile else boto3.Session()
            kafka_client = session.client('kafka', region_name=region)
            
            response = kafka_client.get_bootstrap_brokers(
                ClusterArn=cluster_arn
            )
            
            # Use TLS brokers by default
            brokers = response.get('BootstrapBrokerStringTls', '')
            if not brokers:
                brokers = response.get('BootstrapBrokerString', '')
            
            return brokers.split(',') if brokers else []
            
        except Exception as e:
            click.echo(f"{Fore.RED}Error connecting to cloud cluster: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _get_admin_client(self) -> KafkaAdminClient:
        """Get or create Kafka admin client."""
        if self.admin_client is None:
            bootstrap_servers = self._get_bootstrap_servers()
            
            client_config = {
                'bootstrap_servers': bootstrap_servers,
                'client_id': 'kafka-lens',
                'security_protocol': self.config.get('security_protocol', 'PLAINTEXT')
            }
            
            # Add SASL configuration if specified
            if 'sasl_mechanism' in self.config:
                client_config.update({
                    'sasl_mechanism': self.config['sasl_mechanism'],
                    'sasl_plain_username': self.config.get('sasl_plain_username'),
                    'sasl_plain_password': self.config.get('sasl_plain_password')
                })
            
            # Add SSL configuration if specified
            ssl_config = {}
            if 'ssl_cafile' in self.config:
                ssl_config['cafile'] = self.config['ssl_cafile']
            if 'ssl_certfile' in self.config:
                ssl_config['certfile'] = self.config['ssl_certfile']
            if 'ssl_keyfile' in self.config:
                ssl_config['keyfile'] = self.config['ssl_keyfile']
            
            if ssl_config:
                client_config['ssl_context'] = ssl_config
            
            try:
                self.admin_client = KafkaAdminClient(**client_config)
            except Exception as e:
                click.echo(f"{Fore.RED}Error connecting to Kafka cluster: {e}{Style.RESET_ALL}")
                sys.exit(1)
        
        return self.admin_client
    
    def _get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer for topic analysis."""
        if self.consumer is None:
            bootstrap_servers = self._get_bootstrap_servers()
            
            consumer_config = {
                'bootstrap_servers': bootstrap_servers,
                'security_protocol': self.config.get('security_protocol', 'PLAINTEXT'),
                'auto_offset_reset': 'latest',
                'enable_auto_commit': False
            }
            
            # Add SASL configuration if specified
            if 'sasl_mechanism' in self.config:
                consumer_config.update({
                    'sasl_mechanism': self.config['sasl_mechanism'],
                    'sasl_plain_username': self.config.get('sasl_plain_username'),
                    'sasl_plain_password': self.config.get('sasl_plain_password')
                })
            
            try:
                self.consumer = KafkaConsumer(**consumer_config)
            except Exception as e:
                click.echo(f"{Fore.RED}Error creating Kafka consumer: {e}{Style.RESET_ALL}")
                sys.exit(1)
        
        return self.consumer
    
    def health_check(self):
        """Check cluster health and display summary."""
        click.echo(f"{Fore.CYAN}🔍 Checking cluster health...{Style.RESET_ALL}")
        
        admin_client = self._get_admin_client()
        
        try:
            # Get cluster metadata
            metadata = admin_client.describe_cluster()
            
            # Count brokers
            total_brokers = len(metadata['brokers'])
            connected_brokers = len(metadata['nodes'])
            controller_id = metadata['controller']
            
            # Check for under-replicated partitions
            topics = admin_client.list_topics()
            non_internal_topics = [topic for topic in topics if not topic.startswith('__')]
            
            urp_count = 0
            if non_internal_topics:
                topic_metadata = admin_client.describe_topics(non_internal_topics)
                
                for topic_name, topic_info in topic_metadata.items():
                    for partition_id, partition_info in topic_info.partitions.items():
                        replicas_count = len(partition_info.replicas)
                        isr_count = len(partition_info.isr)
                        if isr_count < replicas_count:
                            urp_count += 1
            
            # Display results
            click.echo(f"\n{Fore.GREEN}📊 Cluster Health Report:{Style.RESET_ALL}")
            click.echo(f"  • Brokers Found: {connected_brokers}/{total_brokers} Online")
            click.echo(f"  • Controller ID: {controller_id}")
            
            if urp_count == 0:
                click.echo(f"  • Under-replicated Partitions: {urp_count} {Fore.GREEN}(OK){Style.RESET_ALL}")
            else:
                click.echo(f"  • Under-replicated Partitions: {urp_count} {Fore.RED}(WARNING){Style.RESET_ALL}")
            
            # Overall health status
            if connected_brokers == total_brokers and urp_count == 0:
                click.echo(f"\n{Fore.GREEN}✅ Cluster is healthy!{Style.RESET_ALL}")
            else:
                click.echo(f"\n{Fore.YELLOW}⚠️  Cluster has issues that need attention.{Style.RESET_ALL}")
                
        except Exception as e:
            click.echo(f"{Fore.RED}Error during health check: {e}{Style.RESET_ALL}")
    
    def check_lag(self):
        """Check consumer group lag."""
        click.echo(f"{Fore.CYAN}🔍 Checking consumer group lag...{Style.RESET_ALL}")
        
        admin_client = self._get_admin_client()
        lag_threshold = self.config.get('lag_threshold', 1000)
        
        try:
            # Get all consumer groups
            groups = admin_client.list_consumer_groups()
            group_lags = {}
            
            for group_id in groups:
                try:
                    # Get committed offsets
                    committed_offsets = admin_client.list_consumer_group_offsets(group_id)
                    
                    if not committed_offsets:
                        continue
                    
                    # Get latest offsets for the same partitions
                    partitions = list(committed_offsets.keys())
                    latest_offsets = admin_client.get_topic_end_offsets(partitions)
                    
                    # Calculate total lag for this group
                    total_lag = 0
                    for tp in partitions:
                        if tp in latest_offsets:
                            committed_offset = committed_offsets[tp].offset
                            latest_offset = latest_offsets[tp]
                            partition_lag = max(0, latest_offset - committed_offset)
                            total_lag += partition_lag
                    
                    group_lags[group_id] = total_lag
                    
                except Exception as e:
                    click.echo(f"{Fore.YELLOW}Warning: Could not check lag for group '{group_id}': {e}{Style.RESET_ALL}")
                    continue
            
            # Display results
            if not group_lags:
                click.echo(f"{Fore.YELLOW}No consumer groups found or accessible.{Style.RESET_ALL}")
                return
            
            click.echo(f"\n{Fore.GREEN}📊 Consumer Group Lag Report:{Style.RESET_ALL}")
            
            high_lag_groups = []
            for group_id, lag in group_lags.items():
                if lag > lag_threshold:
                    high_lag_groups.append((group_id, lag))
                    click.echo(f"  • {group_id}: {Fore.RED}{lag:,} messages{Style.RESET_ALL} (HIGH LAG)")
                else:
                    click.echo(f"  • {group_id}: {Fore.GREEN}{lag:,} messages{Style.RESET_ALL}")
            
            if high_lag_groups:
                click.echo(f"\n{Fore.RED}⚠️  {len(high_lag_groups)} consumer group(s) have high lag!{Style.RESET_ALL}")
            else:
                click.echo(f"\n{Fore.GREEN}✅ All consumer groups are within normal lag thresholds.{Style.RESET_ALL}")
                
        except Exception as e:
            click.echo(f"{Fore.RED}Error during lag check: {e}{Style.RESET_ALL}")
    
    def find_stale_consumers(self):
        """Find stale consumer groups."""
        click.echo(f"{Fore.CYAN}🔍 Finding stale consumer groups...{Style.RESET_ALL}")
        
        admin_client = self._get_admin_client()
        stale_days = self.config.get('stale_consumer_days', 30)
        threshold_ts = (datetime.now() - timedelta(days=stale_days)).timestamp() * 1000
        
        try:
            groups = admin_client.list_consumer_groups()
            stale_groups = []
            
            for group_id in groups:
                try:
                    offsets = admin_client.list_consumer_group_offsets(group_id)
                    
                    if not offsets:
                        # Group has no commits, consider it stale
                        stale_groups.append((group_id, "No commits"))
                        continue
                    
                    # Find the most recent commit timestamp
                    latest_commit = max(offset.commit_timestamp for offset in offsets.values())
                    
                    if latest_commit < threshold_ts:
                        days_old = (datetime.now().timestamp() * 1000 - latest_commit) / (1000 * 60 * 60 * 24)
                        stale_groups.append((group_id, f"{days_old:.1f} days old"))
                        
                except Exception as e:
                    click.echo(f"{Fore.YELLOW}Warning: Could not check group '{group_id}': {e}{Style.RESET_ALL}")
                    continue
            
            # Display results
            if stale_groups:
                click.echo(f"\n{Fore.YELLOW}📊 Found {len(stale_groups)} stale consumer groups:{Style.RESET_ALL}")
                for group_id, reason in stale_groups:
                    click.echo(f"  • {group_id}: {reason}")
            else:
                click.echo(f"\n{Fore.GREEN}✅ No stale consumer groups found.{Style.RESET_ALL}")
                
        except Exception as e:
            click.echo(f"{Fore.RED}Error finding stale consumers: {e}{Style.RESET_ALL}")
    
    def find_unused_topics(self):
        """Find unused topics."""
        click.echo(f"{Fore.CYAN}🔍 Finding unused topics...{Style.RESET_ALL}")
        
        admin_client = self._get_admin_client()
        consumer = self._get_consumer()
        unused_days = self.config.get('unused_topic_days', 90)
        threshold_ts = (datetime.now() - timedelta(days=unused_days)).timestamp() * 1000
        
        try:
            # Get all non-internal topics
            topics = admin_client.list_topics()
            non_internal_topics = [topic for topic in topics if not topic.startswith('__')]
            
            unused_topics = []
            
            for topic in non_internal_topics:
                try:
                    # Get partitions for this topic
                    partitions = consumer.partitions_for_topic(topic)
                    if not partitions:
                        continue
                    
                    # Get end offsets
                    end_offsets = consumer.end_offsets(partitions)
                    
                    # Find the latest message timestamp across all partitions
                    latest_timestamp = 0
                    for partition in partitions:
                        if end_offsets[partition] > 0:
                            # Seek to the last message
                            consumer.seek_to_end(partition)
                            consumer.seek(partition, end_offsets[partition] - 1)
                            
                            # Poll for one message to get timestamp
                            messages = consumer.poll(timeout_ms=1000)
                            for tp, msgs in messages.items():
                                if tp.partition == partition and msgs:
                                    latest_timestamp = max(latest_timestamp, msgs[0].timestamp)
                    
                    if latest_timestamp > 0 and latest_timestamp < threshold_ts:
                        days_old = (datetime.now().timestamp() * 1000 - latest_timestamp) / (1000 * 60 * 60 * 24)
                        unused_topics.append((topic, f"{days_old:.1f} days old"))
                        
                except Exception as e:
                    click.echo(f"{Fore.YELLOW}Warning: Could not check topic '{topic}': {e}{Style.RESET_ALL}")
                    continue
            
            # Display results
            if unused_topics:
                click.echo(f"\n{Fore.YELLOW}📊 Found {len(unused_topics)} unused topics:{Style.RESET_ALL}")
                for topic, reason in unused_topics:
                    click.echo(f"  • {topic}: {reason}")
            else:
                click.echo(f"\n{Fore.GREEN}✅ No unused topics found.{Style.RESET_ALL}")
                
        except Exception as e:
            click.echo(f"{Fore.RED}Error finding unused topics: {e}{Style.RESET_ALL}")
    
    def delete_consumer_group(self, group_name: str):
        """Delete a consumer group."""
        admin_client = self._get_admin_client()
        
        # Safety prompt
        confirm = click.prompt(
            f"Are you sure you want to delete consumer group '{group_name}'? This cannot be undone. [y/N]",
            default='N'
        )
        
        if confirm.lower() != 'y':
            click.echo("Operation cancelled.")
            return
        
        try:
            admin_client.delete_consumer_groups([group_name])
            click.echo(f"{Fore.GREEN}✅ Successfully deleted consumer group '{group_name}'.{Style.RESET_ALL}")
        except Exception as e:
            click.echo(f"{Fore.RED}Error deleting consumer group: {e}{Style.RESET_ALL}")
    
    def delete_topic(self, topic_name: str):
        """Delete a topic."""
        admin_client = self._get_admin_client()
        
        # Safety prompt
        confirm = click.prompt(
            f"Are you sure you want to delete topic '{topic_name}'? This cannot be undone. [y/N]",
            default='N'
        )
        
        if confirm.lower() != 'y':
            click.echo("Operation cancelled.")
            return
        
        try:
            admin_client.delete_topics([topic_name])
            click.echo(f"{Fore.GREEN}✅ Successfully deleted topic '{topic_name}'.{Style.RESET_ALL}")
        except Exception as e:
            click.echo(f"{Fore.RED}Error deleting topic: {e}{Style.RESET_ALL}")
    
    def close(self):
        """Close connections."""
        if self.admin_client:
            self.admin_client.close()
        if self.consumer:
            self.consumer.close()


@click.group()
@click.option('--config', '-c', default='config.yml', help='Path to configuration file')
@click.pass_context
def cli(ctx, config):
    """Kafka Lens - Mission control for your Kafka cluster."""
    ctx.ensure_object(dict)
    ctx.obj['commander'] = KafkaLens(config)


@cli.command()
@click.pass_context
def health_check(ctx):
    """Check cluster health and display summary."""
    commander = ctx.obj['commander']
    commander.health_check()


@cli.command()
@click.pass_context
def check_lag(ctx):
    """Check consumer group lag."""
    commander = ctx.obj['commander']
    commander.check_lag()


@cli.group()
def find():
    """Find unused resources."""
    pass


@find.command('stale-consumers')
@click.pass_context
def find_stale_consumers(ctx):
    """Find stale consumer groups."""
    commander = ctx.obj['commander']
    commander.find_stale_consumers()


@find.command('unused-topics')
@click.pass_context
def find_unused_topics(ctx):
    """Find unused topics."""
    commander = ctx.obj['commander']
    commander.find_unused_topics()


@cli.group()
def delete():
    """Delete resources."""
    pass


@delete.command('group')
@click.argument('group_name')
@click.pass_context
def delete_group(ctx, group_name):
    """Delete a consumer group."""
    commander = ctx.obj['commander']
    commander.delete_consumer_group(group_name)


@delete.command('topic')
@click.argument('topic_name')
@click.pass_context
def delete_topic(ctx, topic_name):
    """Delete a topic."""
    commander = ctx.obj['commander']
    commander.delete_topic(topic_name)


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        click.echo(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        sys.exit(1)
