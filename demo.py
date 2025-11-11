#!/usr/bin/env python3
"""
Demo script showing the Kafka Lens structure and usage.
This script doesn't require the actual dependencies to be installed.
"""

import sys

def print_banner():
    """Print the tool banner."""
    print("=" * 60)
    print("🔍 KAFKA LENS - DEMO")
    print("=" * 60)
    print()

def print_commands():
    """Print available commands."""
    print("📋 AVAILABLE COMMANDS:")
    print()
    print("  🔍 Health Check:")
    print("     python3 kafka_lens.py health-check")
    print("     - Check cluster health and broker status")
    print("     - Identify under-replicated partitions")
    print("     - Display controller information")
    print()
    print("  📊 Lag Monitoring:")
    print("     python3 kafka_lens.py check-lag")
    print("     - Monitor consumer group lag")
    print("     - Highlight high-lag groups")
    print("     - Provide actionable insights")
    print()
    print("  🔍 Resource Discovery:")
    print("     python3 kafka_lens.py find stale-consumers")
    print("     - Find stale consumer groups")
    print("     - Identify abandoned consumers")
    print()
    print("     python3 kafka_lens.py find unused-topics")
    print("     - Find unused topics")
    print("     - Identify cleanup candidates")
    print()
    print("  🗑️  Resource Cleanup:")
    print("     python3 kafka_lens.py delete group <name>")
    print("     - Delete consumer groups (with confirmation)")
    print()
    print("     python3 kafka_lens.py delete topic <name>")
    print("     - Delete topics (with confirmation)")
    print()

def print_config_example():
    """Print configuration example."""
    print("⚙️  CONFIGURATION EXAMPLE (config.yml):")
    print()
    print("```yaml")
    print("# MSK Configuration (preferred)")
    print("msk_cluster_arn: \"arn:aws:kafka:us-west-2:123456789012:cluster/my-cluster/...\"")
    print()
    print("# Static Broker Configuration (fallback)")
    print("bootstrap_servers: \"localhost:9092\"")
    print()
    print("# Security Configuration")
    print("security_protocol: \"PLAINTEXT\"")
    print("sasl_mechanism: \"PLAIN\"  # If using SASL")
    print("sasl_plain_username: \"your-username\"")
    print("sasl_plain_password: \"your-password\"")
    print()
    print("# Health Check Thresholds")
    print("lag_threshold: 1000")
    print("stale_consumer_days: 30")
    print("unused_topic_days: 90")
    print("```")
    print()

def print_installation():
    """Print installation instructions."""
    print("📦 INSTALLATION:")
    print()
    print("1. Install dependencies:")
    print("   pip3 install -r requirements.txt")
    print()
    print("2. Configure your cluster:")
    print("   cp config.yml my-config.yml")
    print("   # Edit my-config.yml with your cluster details")
    print()
    print("3. Test connection:")
    print("   python3 test_connection.py")
    print()
    print("4. Run health check:")
    print("   python3 kafka_lens.py health-check")
    print()

def print_features():
    """Print key features."""
    print("✨ KEY FEATURES:")
    print()
    print("  • 🔍 Comprehensive health monitoring")
    print("  • 📊 Real-time lag analysis")
    print("  • 🧹 Automated resource cleanup")
    print("  • ☁️  Amazon MSK integration")
    print("  • 🔒 Full security support (SSL, SASL, IAM)")
    print("  • 🎨 Beautiful, color-coded output")
    print("  • ⚡ One-line commands for complex operations")
    print("  • 🛡️  Safe deletion with confirmation prompts")
    print()

def main():
    """Main demo function."""
    print_banner()
    print_features()
    print_commands()
    print_config_example()
    print_installation()
    
    print("🎉 Ready to manage your Kafka cluster like a pro!")
    print("   For detailed documentation, see README.md")

if __name__ == "__main__":
    main()
