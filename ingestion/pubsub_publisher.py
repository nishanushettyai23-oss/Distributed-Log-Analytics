"""
Pub/Sub Publisher for Log Ingestion
Simulates microservice logs and publishes them to Google Cloud Pub/Sub.
"""

import json
import time
import random
from datetime import datetime
from google.cloud import pubsub_v1

# Configuration Placeholders
PROJECT_ID = "your-project-id"
TOPIC_ID = "infrastructure-logs"

def generate_log():
    """Generates a realistic log entry."""
    services = ["web-server", "payment-gateway", "auth-service", "database"]
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    
    # Simulate realistic log distribution
    level = random.choices(levels, weights=[70, 15, 10, 5])[0]
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": random.choice(services),
        "level": level,
        "message": f"Simulated {level} message from {random.choice(services)}",
        "trace_id": f"trace-{random.randint(1000, 9999)}"
    }

def publish_logs(project_id, topic_id):
    """Publishes continuous logs to Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    print(f"Starting publisher on {topic_path}...")
    
    try:
        while True:
            log_data = generate_log()
            # Serialize payload as JSON
            data_str = json.dumps(log_data)
            data_bytes = data_str.encode("utf-8")
            
            # Publish message
            future = publisher.publish(topic_path, data_bytes)
            print(f"Published message ID: {future.result()} | Data: {data_str}")
            
            # Sleep to simulate real traffic
            time.sleep(random.uniform(0.1, 1.0))
            
    except KeyboardInterrupt:
        print("Publisher stopped.")

if __name__ == "__main__":
    publish_logs(PROJECT_ID, TOPIC_ID)
