#!/bin/bash
# GCP Environment Setup Script
# NOTE: Replace 'your-project-id' with your actual GCP Project ID.
# DO NOT RUN WITHOUT CONFIGURATION.

PROJECT_ID="your-project-id"
REGION="us-central1"

# 1. Enable necessary APIs
# gcloud services enable \
#     pubsub.googleapis.com \
#     dataflow.googleapis.com \
#     dataproc.googleapis.com \
#     bigquery.googleapis.com \
#     cloudfunctions.googleapis.com \
#     --project $PROJECT_ID

# 2. Create Cloud Storage buckets for Data Lake and temp files
# gsutil mb -l $REGION gs://$PROJECT_ID-raw-logs/
# gsutil mb -l $REGION gs://$PROJECT_ID-dataflow-temp/

# 3. Deploy Cloud Function for alerting
# gcloud functions deploy alert-function \
#     --runtime python39 \
#     --trigger-http \
#     --allow-unauthenticated \
#     --source ../alerting/ \
#     --entry-point alert_handler \
#     --project $PROJECT_ID

echo "Uncomment the commands above to provision GCP resources."
