#!/bin/bash

# ============================================================
# Distributed Batch Log Analytics - GCP Setup Script
# ============================================================
# This script automates the setup of Google Cloud resources
# for the batch log analytics system.
#
# IMPORTANT: Set PROJECT_ID before running!
# ============================================================

# CONFIGURATION - CHANGE THESE VALUES
PROJECT_ID="your-project-id"  # ← SET YOUR PROJECT ID
REGION="us-central1"
CLUSTER_NAME="log-analytics-cluster"
WORKER_COUNT=2

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# ============================================================
# Step 0: Validation
# ============================================================

if [ "$PROJECT_ID" == "your-project-id" ]; then
    print_error "PROJECT_ID not configured!"
    echo "Please edit this script and set PROJECT_ID to your actual GCP project ID"
    echo "You can find your project ID by running: gcloud config get-value project"
    exit 1
fi

print_step "Using GCP Project: $PROJECT_ID"
print_step "Using Region: $REGION"

# Verify gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# ============================================================
# Step 1: Set Active Project
# ============================================================

print_step "Setting active GCP project..."
gcloud config set project $PROJECT_ID

# ============================================================
# Step 2: Enable Required APIs
# ============================================================

print_step "Enabling Google Cloud APIs..."
gcloud services enable \
    storage.googleapis.com \
    dataproc.googleapis.com \
    bigquery.googleapis.com \
    compute.googleapis.com \
    --project=$PROJECT_ID

if [ $? -eq 0 ]; then
    echo "  ✓ APIs enabled successfully"
else
    print_error "Failed to enable APIs"
    exit 1
fi

# ============================================================
# Step 3: Create Cloud Storage Buckets
# ============================================================

print_step "Creating Cloud Storage buckets..."

# Raw logs bucket
BUCKET_LOGS="gs://${PROJECT_ID}-raw-logs"
if gsutil ls $BUCKET_LOGS &> /dev/null; then
    echo "  ✓ Bucket already exists: $BUCKET_LOGS"
else
    gsutil mb -l $REGION $BUCKET_LOGS
    echo "  ✓ Created bucket: $BUCKET_LOGS"
fi

# Processed results bucket
BUCKET_RESULTS="gs://${PROJECT_ID}-processed-logs"
if gsutil ls $BUCKET_RESULTS &> /dev/null; then
    echo "  ✓ Bucket already exists: $BUCKET_RESULTS"
else
    gsutil mb -l $REGION $BUCKET_RESULTS
    echo "  ✓ Created bucket: $BUCKET_RESULTS"
fi

# ============================================================
# Step 4: Create BigQuery Dataset
# ============================================================

print_step "Creating BigQuery dataset..."

# Check if dataset exists
if bq ls -d $PROJECT_ID:logs_dataset &> /dev/null; then
    echo "  ✓ Dataset already exists: logs_dataset"
else
    bq mk --dataset \
        --description="Log Analytics Dataset" \
        --location=US \
        logs_dataset
    echo "  ✓ Created dataset: logs_dataset"
fi

# ============================================================
# Step 5: Create BigQuery Tables
# ============================================================

print_step "Creating BigQuery tables..."

# Function to create table
create_table() {
    local table_name=$1
    local schema=$2
    
    if bq ls $PROJECT_ID:logs_dataset.$table_name &> /dev/null; then
        echo "  ✓ Table already exists: $table_name"
    else
        bq mk --table \
            logs_dataset.$table_name \
            "$schema"
        echo "  ✓ Created table: $table_name"
    fi
}

# Define table schemas
ERROR_FREQUENCY_SCHEMA="service:STRING,error_count:INTEGER"
PROCESSED_LOGS_SCHEMA="timestamp:TIMESTAMP,level:STRING,service:STRING,node:STRING,message:STRING,request_id:STRING,duration_ms:INTEGER,status_code:INTEGER"
ANOMALIES_SCHEMA="service:STRING,error_count:INTEGER,threshold:FLOAT,severity:STRING,deviation:FLOAT,timestamp:TIMESTAMP"

create_table "error_frequency" "$ERROR_FREQUENCY_SCHEMA"
create_table "processed_logs" "$PROCESSED_LOGS_SCHEMA"
create_table "anomalies" "$ANOMALIES_SCHEMA"

# ============================================================
# Step 6: Create Dataproc Cluster (Optional)
# ============================================================

read -p "Create Dataproc cluster for batch processing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Creating Dataproc cluster: $CLUSTER_NAME..."
    
    if gcloud dataproc clusters describe $CLUSTER_NAME --region=$REGION &> /dev/null; then
        echo "  ✓ Cluster already exists: $CLUSTER_NAME"
    else
        gcloud dataproc clusters create $CLUSTER_NAME \
            --project=$PROJECT_ID \
            --region=$REGION \
            --master-machine-type n1-standard-2 \
            --worker-machine-type n1-standard-2 \
            --num-workers $WORKER_COUNT \
            --python-version 3 \
            --enable-component-gateway
        
        if [ $? -eq 0 ]; then
            echo "  ✓ Cluster created successfully"
        else
            print_error "Failed to create cluster"
            exit 1
        fi
    fi
else
    print_warning "Skipped Dataproc cluster creation"
fi

# ============================================================
# Step 7: Setup Application Default Credentials
# ============================================================

print_step "Setting up Application Default Credentials..."

# Check if credentials already exist
if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ] || [ -f "$APPDATA/gcloud/application_default_credentials.json" ]; then
    echo "  ✓ Credentials already configured"
else
    echo "  Running: gcloud auth application-default login"
    gcloud auth application-default login
fi

# ============================================================
# Step 8: Configuration Summary
# ============================================================

print_step "Configuration Summary"
echo ""
echo "Project ID:           $PROJECT_ID"
echo "Region:               $REGION"
echo "Raw Logs Bucket:      $BUCKET_LOGS"
echo "Results Bucket:       $BUCKET_RESULTS"
echo "BigQuery Dataset:     logs_dataset"
echo "Dataproc Cluster:     $CLUSTER_NAME"
echo ""

# ============================================================
# Step 9: Next Steps
# ============================================================

print_step "Setup Complete! Next Steps:"
echo ""
echo "1. Build the Docker image:"
echo "   docker build -t distributed-log-analytics:latest ."
echo ""
echo "2. Place the full HDFS dataset at:"
echo "   dataset/HDFS_full/HDFS.log"
echo ""
echo "3. Validate and upload the large dataset:"
echo "   python deployment/prepare_large_dataset.py --local-path dataset/HDFS_full/HDFS.log --gcs-path gs://${PROJECT_ID}-raw-logs/loghub/hdfs/full/HDFS.log"
echo ""
echo "4. Upload the Dataproc Spark job:"
echo "   gsutil cp batch_processing/spark_job.py gs://${PROJECT_ID}-spark-code/jobs/spark_job.py"
echo ""
echo "5. Run the Dataproc job using docs/GCP_DEPLOYMENT_GUIDE.md"
echo ""
