# GCP Connection Guide - Quick Reference

## 🎯 Three-Step Connection

### Step 1: Install gcloud CLI (2 minutes)
```powershell
# Download: https://cloud.google.com/sdk/docs/install-gcloud-cli#windows
# Run installer and restart PowerShell

# Verify
gcloud --version
```

### Step 2: Authenticate (1 minute)
```powershell
# Opens browser for login
gcloud auth login

# Confirm successful
gcloud auth list
```

### Step 3: Automated Setup (2 minutes)
```powershell
# From project directory
python deployment/setup_gcp_helper.py

# Answers all prompts and sets up:
# ✓ Cloud Storage buckets
# ✓ BigQuery dataset & tables
# ✓ Credentials
```

---

## 📝 After Setup: Update 3 Configuration Files

### File 1: batch_processing/spark_job.py
Change line ~11:
```python
PROJECT_ID = "YOUR_PROJECT_ID"  # Replace with your actual project ID
```

### File 2: analytics/anomaly_detection.py
Change line ~11:
```python
PROJECT_ID = "YOUR_PROJECT_ID"  # Replace with your actual project ID
```

### File 3: streaming/pipeline.py
Change line ~15:
```python
GCS_BUCKET = "YOUR_PROJECT_ID-raw-logs"  # Replace with your actual project ID
```

**Find your Project ID:**
```powershell
gcloud config get-value project
```

---

## 🚀 Run Your First Batch Job

```powershell
# 1. Generate sample logs
python ingestion/log_generator.py

# 2. Upload to Cloud Storage
gsutil cp data/sample_logs.json gs://YOUR_PROJECT_ID-raw-logs/logs/

# 3. Run Spark analytics
spark-submit batch_processing/spark_job.py

# 4. Analyze results
python analytics/anomaly_detection.py
```

---

## ✅ Verification Checklist

```powershell
# Check Cloud Storage
gsutil ls

# Check BigQuery
bq ls logs_dataset

# Check authentication
gcloud auth list

# Check active project
gcloud config get-value project
```

---

## 📚 Full Guides Available

- **`docs/QUICK_START_WINDOWS.md`** - Detailed Windows setup
- **`docs/GCP_SETUP_GUIDE.md`** - Complete GCP documentation
- **`deployment/setup_gcp_helper.py`** - Automated setup script

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| "gcloud not found" | Reinstall from: https://cloud.google.com/sdk/docs/install-gcloud-cli |
| "Permission denied" | Run: `gcloud auth login` again |
| "Bucket not found" | Verify project ID: `gcloud config get-value project` |
| "No credentials" | Run: `gcloud auth application-default login` |

---

## 💰 Cost-Saving Tips

1. **Use Preemptible VMs** (80% cheaper):
   ```powershell
   gcloud dataproc clusters create my-cluster --preemptible-workers=4
   ```

2. **Delete idle resources**:
   ```powershell
   gcloud dataproc clusters delete CLUSTER_NAME
   gsutil rb gs://bucket-name/
   ```

3. **Set storage lifecycle** (archive old logs):
   ```powershell
   gsutil lifecycle set lifecycle.json gs://bucket-name/
   ```

---

## 📊 Architecture Overview

```
Your Local Machine
    ↓
gcloud CLI (authentication)
    ↓
Google Cloud Platform
├── Cloud Storage (Raw Logs)
├── Spark/Dataproc (Processing)
└── BigQuery (Results)
```

---

## 🔗 Useful Links

- [Google Cloud Console](https://console.cloud.google.com)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)

---

## ❓ Need More Help?

1. Check specific guides:
   - Windows setup: `docs/QUICK_START_WINDOWS.md`
   - Full GCP guide: `docs/GCP_SETUP_GUIDE.md`

2. View setup script options:
   - `deployment/setup_gcp_helper.py` - Python helper
   - `deployment/setup_gcp.sh` - Bash script

3. Use config template:
   - `config/gcp_config_template.py` - Centralized configuration

---

**You're ready to go!** Start with Step 1 above and follow through Step 3. You'll have everything connected in ~5 minutes.
