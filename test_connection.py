#!/usr/bin/env python3
"""
Simple test script to verify Kafka connection and configuration.
"""

import sys
import yaml
from kafka_lens import KafkaLens

def test_connection():
    """Test the Kafka connection with the current configuration."""
    try:
        print("🔍 Testing Kafka connection...")
        
        # Load configuration
        lens = KafkaLens()
        
        # Test admin client connection
        admin_client = lens._get_admin_client()
        print("✅ Admin client connection successful")
        
        # Test basic cluster info
        metadata = admin_client.describe_cluster()
        print(f"✅ Cluster metadata retrieved: {len(metadata['brokers'])} brokers found")
        
        # Test consumer connection
        consumer = lens._get_consumer()
        print("✅ Consumer connection successful")
        
        # Clean up
        lens.close()
        
        print("\n🎉 All connections successful! Your Kafka Lens is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check your config.yml file")
        print("2. Verify your Kafka cluster is running")
        print("3. Check network connectivity")
        print("4. Verify authentication credentials")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
