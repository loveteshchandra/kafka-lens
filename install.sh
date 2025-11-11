#!/bin/bash
# Installation script for Kafka Lens

echo "🔍 Installing Kafka Lens..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
chmod +x kafka_lens.py
chmod +x test_connection.py
chmod +x example_usage.py

echo "✅ Scripts made executable"

# Create symlink for easy access
if [ -w /usr/local/bin ]; then
    ln -sf "$(pwd)/kafka_lens.py" /usr/local/bin/kl
    echo "✅ Created symlink: kl -> kafka_lens.py"
else
    echo "⚠️  Could not create symlink in /usr/local/bin (permission denied)"
    echo "   You can still run: python3 $(pwd)/kafka_lens.py"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Configure your Kafka cluster in config.yml"
echo "2. Test the connection: python3 test_connection.py"
echo "3. Run health check: python3 kafka_lens.py health-check"
echo ""
echo "For more information, see README.md"