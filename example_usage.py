#!/usr/bin/env python3
"""
Example usage of Kafka Lens programmatically.
"""

from kafka_lens import KafkaLens

def main():
    """Example of using Kafka Lens programmatically."""
    
    # Initialize the lens
    lens = KafkaLens("config.yml")
    
    try:
        print("🚀 Running Kafka Lens examples...\n")
        
        # 1. Health Check
        print("1. Running health check...")
        lens.health_check()
        print()
        
        # 2. Check Lag
        print("2. Checking consumer group lag...")
        lens.check_lag()
        print()
        
        # 3. Find Stale Consumers
        print("3. Finding stale consumer groups...")
        lens.find_stale_consumers()
        print()
        
        # 4. Find Unused Topics
        print("4. Finding unused topics...")
        lens.find_unused_topics()
        print()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
    
    finally:
        # Always close connections
        lens.close()

if __name__ == "__main__":
    main()
