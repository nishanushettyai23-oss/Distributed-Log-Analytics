"""
Anomaly Detection Script
Queries BigQuery for error rates and flags anomalies based on a static threshold.
Designed to run periodically via Cloud Scheduler.
"""

from google.cloud import bigquery
import requests
import json

# Configuration Placeholders
PROJECT_ID = "your-project-id"
DATASET_ID = "logs_dataset"
ALERT_WEBHOOK_URL = "https://us-central1-your-project-id.cloudfunctions.net/alert-function"
THRESHOLD = 100 # Alert if more than 100 errors in the last hour

def check_anomalies():
    client = bigquery.Client(project=PROJECT_ID)

    # Query to count errors in the last 1 hour
    query = f"""
        SELECT count(*) as error_count
        FROM `{PROJECT_ID}.{DATASET_ID}.error_logs`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
    """

    query_job = client.query(query)
    results = query_job.result()

    for row in results:
        error_count = row.error_count
        print(f"Current error count for the last hour: {error_count}")
        
        if error_count > THRESHOLD:
            trigger_alert(error_count)

def trigger_alert(count):
    """Triggers an alert by calling the Alerting Cloud Function."""
    payload = {
        "metric": "error_rate",
        "value": count,
        "threshold": THRESHOLD,
        "message": f"CRITICAL: Error rate exceeded threshold. Current count: {count}"
    }
    
    print(f"Triggering alert webhook: {payload}")
    
    # Make POST request to the Cloud Function
    try:
        response = requests.post(ALERT_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("Alert triggered successfully.")
    except Exception as e:
        print(f"Failed to trigger alert: {e}")

if __name__ == "__main__":
    check_anomalies()
