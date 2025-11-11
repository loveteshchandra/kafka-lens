# Kafka Lens 🔍

A command-line interface (CLI) tool that provides Kafka administrators with simple, one-line commands to diagnose cluster health, pinpoint consumer group lag, and clean up stale resources on Apache Kafka / Amazon MSK clusters.

## Features

- **🔍 Health Check**: Quick cluster overview with broker status and under-replicated partition detection
- **📊 Lag Monitoring**: Identify consumer groups falling behind in message processing
- **🧹 Resource Cleanup**: Find and safely delete stale consumer groups and unused topics
- **☁️ MSK Integration**: Seamless Amazon MSK cluster discovery and connection
- **🔒 Security Support**: Full support for SSL, SASL, and AWS IAM authentication
- **🎨 Beautiful Output**: Color-coded, easy-to-read command output

## Installation

### Prerequisites

- Python 3.7 or higher
- Access to a Kafka cluster (local, cloud, or Amazon MSK)

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd kafka-lens

# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x kafka_lens.py
```

### Development Install

```bash
# Install in development mode
pip install -e .
```

## Configuration

Create a `config.yml` file in your working directory:

```yaml
# MSK Configuration (preferred method)
msk_cluster_arn: "arn:aws:kafka:us-west-2:123456789012:cluster/my-cluster/12345678-1234-1234-1234-123456789012-1"

# Static Broker Configuration (fallback)
bootstrap_servers: "localhost:9092"

# Security Configuration
security_protocol: "PLAINTEXT"  # Options: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
sasl_mechanism: "PLAIN"  # Uncomment if using SASL
sasl_plain_username: "your-username"
sasl_plain_password: "your-password"

# Health Check Thresholds
lag_threshold: 1000  # Alert if consumer group lag exceeds this number
stale_consumer_days: 30  # Consider consumers stale after this many days
unused_topic_days: 90  # Consider topics unused after this many days

# AWS Configuration (for MSK)
aws_region: "us-west-2"
aws_profile: "default"  # Optional: specify AWS profile to use
```

## Usage

### Basic Commands

```bash
# Check cluster health
python kafka_lens.py health-check

# Check consumer group lag
python kafka_lens.py check-lag

# Find stale consumer groups
python kafka_lens.py find stale-consumers

# Find unused topics
python kafka_lens.py find unused-topics

# Delete a consumer group (with confirmation prompt)
python kafka_lens.py delete group my-group

# Delete a topic (with confirmation prompt)
python kafka_lens.py delete topic my-topic
```

### Using the Short Alias

If installed via pip, you can use the short alias:

```bash
# Using the short alias
kl health-check
kl check-lag
kl find stale-consumers
```

### Custom Configuration

```bash
# Use a custom configuration file
python kafka_lens.py --config /path/to/my-config.yml health-check
```

## Command Reference

### `health-check`
Provides a high-level summary of the cluster's operational status:
- Broker connectivity status
- Controller identification
- Under-replicated partition count
- Overall cluster health assessment

### `check-lag`
Identifies consumer groups that are falling behind in processing messages:
- Lists all consumer groups with their current lag
- Highlights groups exceeding the configured threshold
- Provides actionable insights for lag management

### `find stale-consumers`
Identifies consumer groups that haven't committed offsets recently:
- Configurable staleness threshold (default: 30 days)
- Safe identification without affecting active consumers
- Helps clean up abandoned consumer groups

### `find unused-topics`
Identifies topics that haven't received messages recently:
- Configurable unused threshold (default: 90 days)
- Analyzes message timestamps across all partitions
- Helps identify topics that can be safely removed

### `delete group <name>`
Safely deletes a consumer group:
- Requires explicit confirmation
- Cannot be undone once executed
- Provides clear feedback on success/failure

### `delete topic <name>`
Safely deletes a topic:
- Requires explicit confirmation
- Cannot be undone once executed
- Provides clear feedback on success/failure

## Security

The tool supports various security configurations:

### SSL/TLS
```yaml
security_protocol: "SSL"
ssl_cafile: "/path/to/ca-cert"
ssl_certfile: "/path/to/client-cert"
ssl_keyfile: "/path/to/client-key"
```

### SASL Authentication
```yaml
security_protocol: "SASL_SSL"
sasl_mechanism: "PLAIN"
sasl_plain_username: "your-username"
sasl_plain_password: "your-password"
```

### Amazon MSK
```yaml
msk_cluster_arn: "arn:aws:kafka:us-west-2:123456789012:cluster/my-cluster/12345678-1234-1234-1234-123456789012-1"
aws_region: "us-west-2"
aws_profile: "default"  # Optional
```

## Examples

### Daily Health Check
```bash
# Quick morning health check
kl health-check
```

### Lag Monitoring
```bash
# Check for high-lag consumer groups
kl check-lag
```

### Cleanup Stale Resources
```bash
# Find stale consumers
kl find stale-consumers

# Find unused topics
kl find unused-topics

# Clean up (with confirmation prompts)
kl delete group stale-consumer-group
kl delete topic unused-topic
```

### MSK Cluster Management
```bash
# Using MSK cluster ARN (no need to specify brokers)
kl --config msk-config.yml health-check
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check your `bootstrap_servers` configuration
2. **Authentication Failed**: Verify your SASL credentials or SSL certificates
3. **MSK Connection Issues**: Ensure your AWS credentials are configured and the cluster ARN is correct
4. **Permission Denied**: Verify your Kafka user has the necessary permissions

### Debug Mode

For detailed error information, check the error messages in the output. The tool provides specific error messages for different failure scenarios.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
