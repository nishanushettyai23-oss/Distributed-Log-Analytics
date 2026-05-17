#!/bin/bash
# Script to create Pub/Sub topic and subscription using gcloud CLI

PROJECT_ID="your-project-id"
TOPIC_ID="infrastructure-logs"
SUBSCRIPTION_ID="infrastructure-logs-sub"

# Create the topic
gcloud pubsub topics create $TOPIC_ID --project=$PROJECT_ID

# Create a pull subscription for testing/streaming
gcloud pubsub subscriptions create $SUBSCRIPTION_ID \
    --topic=$TOPIC_ID \
    --project=$PROJECT_ID

echo "Created topic: $TOPIC_ID and subscription: $SUBSCRIPTION_ID"
