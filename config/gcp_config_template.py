# GCP Configuration Template

Copy this file to `config/gcp_config.py` and fill in your values.
Then import this in your Python scripts instead of hardcoding values.

## Usage Example:

```python
from config.gcp_config import GCP_CONFIG

project_id = GCP_CONFIG['PROJECT_ID']
bucket_raw = GCP_CONFIG['BUCKET_RAW_LOGS']
dataset = GCP_CONFIG['BIGQUERY_DATASET']
```

---

# Google Cloud Platform Configuration

## Step 1: Find Your Project ID

Run in PowerShell:
```powershell
gcloud config get-value project
```

Or view in Google Cloud Console: https://console.cloud.google.com/home

## Step 2: Fill in the values below

```python
# ============================================================
# GOOGLE CLOUD PLATFORM CONFIGURATION
# ============================================================

GCP_CONFIG = {
    # Your GCP Project ID (find it in Google Cloud Console)
    'PROJECT_ID': 'your-project-id-here',
    
    # Region for resources
    'REGION': 'us-central1',
    
    # ============================================================
    # CLOUD STORAGE CONFIGURATION
    # ============================================================
    
    'BUCKET_RAW_LOGS': 'gs://your-project-id-here-raw-logs',
    'BUCKET_PROCESSED': 'gs://your-project-id-here-processed-logs',
    'LOGS_PREFIX': 'logs/',
    
    # ============================================================
    # BIGQUERY CONFIGURATION
    # ============================================================
    
    'BIGQUERY_DATASET': 'logs_dataset',
    'BIGQUERY_TABLES': {
        'error_frequency': 'error_frequency',
        'processed_logs': 'processed_logs',
        'anomalies': 'anomalies',
    },
    
    # ============================================================
    # SPARK CONFIGURATION
    # ============================================================
    
    'SPARK_JOB_NAME': 'log-analytics-batch',
    'SPARK_LOG_LEVEL': 'WARN',  # DEBUG, INFO, WARN, ERROR
    
    # ============================================================
    # DATAPROC CONFIGURATION (for cloud execution)
    # ============================================================
    
    'DATAPROC_CLUSTER_NAME': 'log-analytics-cluster',
    'DATAPROC_CLUSTER_SIZE': 2,  # Number of workers
    'DATAPROC_MACHINE_TYPE': 'n1-standard-2',
    
    # ============================================================
    # ANOMALY DETECTION CONFIGURATION
    # ============================================================
    
    'ANOMALY_THRESHOLD_MULTIPLIER': 2.0,  # 2.0 = 2x standard deviation
    'ERROR_ALERT_WEBHOOK': 'https://your-webhook-url-here.com/alerts',
}

# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def get_gcs_path(bucket_type, path=''):
    """Get full GCS path"""
    bucket = GCP_CONFIG.get(f'BUCKET_{bucket_type.upper()}')
    if path:
        return f"{bucket}/{path}"
    return bucket

def get_bigquery_table(table_name):
    """Get full BigQuery table reference"""
    project = GCP_CONFIG['PROJECT_ID']
    dataset = GCP_CONFIG['BIGQUERY_DATASET']
    table = GCP_CONFIG['BIGQUERY_TABLES'].get(table_name, table_name)
    return f"{project}:{dataset}.{table}"

# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == '__main__':
    # Print configuration
    print("GCP Configuration:")
    print(f"  Project ID: {GCP_CONFIG['PROJECT_ID']}")
    print(f"  Region: {GCP_CONFIG['REGION']}")
    print(f"  Raw Logs Bucket: {GCP_CONFIG['BUCKET_RAW_LOGS']}")
    print(f"  Processed Logs Bucket: {GCP_CONFIG['BUCKET_PROCESSED']}")
    print(f"  BigQuery Dataset: {GCP_CONFIG['BIGQUERY_DATASET']}")
    print()
    print("Example paths:")
    print(f"  Raw logs path: {get_gcs_path('raw_logs', 'logs/')}*.json")
    print(f"  Error frequency table: {get_bigquery_table('error_frequency')}")
```

## Step 3: Create config directory and file

```powershell
# Create config directory if it doesn't exist
mkdir config

# Create gcp_config.py in config directory
# Copy the content above into config/gcp_config.py
```

## Step 4: Update your Python scripts

Instead of:
```python
PROJECT_ID = "your-project-id"
```

Use:
```python
from config.gcp_config import GCP_CONFIG, get_bigquery_table

project_id = GCP_CONFIG['PROJECT_ID']
table = get_bigquery_table('error_frequency')
```

This keeps your configuration centralized and easy to manage!
