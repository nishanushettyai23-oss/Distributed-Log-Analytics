"""
Cloud Function for Alerting.
Receives webhook payloads from anomaly detection and integrates with notification channels (e.g., Slack, Email).
"""

import json
import os

def alert_handler(request):
    """
    HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
    Returns:
        A success message or error string.
    """
    request_json = request.get_json(silent=True)
    
    if request_json and 'message' in request_json:
        alert_message = request_json['message']
        metric_value = request_json.get('value', 'Unknown')
        
        # Here you would integrate with Slack API, SendGrid, or PagerDuty.
        # For simulation, we just print the alert to Cloud Logging.
        print(f"ALERT RECEIVED: {alert_message}")
        print(f"Metric Value: {metric_value}")
        
        # Example: Slack Webhook Integration (Placeholder)
        # slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        # requests.post(slack_webhook_url, json={"text": alert_message})
        
        return "Alert processed successfully", 200
    else:
        return "Invalid request format. 'message' field required.", 400
