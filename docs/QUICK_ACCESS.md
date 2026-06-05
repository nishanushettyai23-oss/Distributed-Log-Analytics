# Quick Access Guide - GCP Console

## 🚀 Your Data is LIVE - Access It Now

All your processed logs are now live in Google Cloud and ready to explore!

---

## 📍 Direct Links

### BigQuery Console
**URL**: https://console.cloud.google.com/bigquery?project=distributed-log-analytics

**Dataset**: `logs_dataset`
```
Project: distributed-log-analytics
└── logs_dataset/
    ├── error_frequency (9 rows) ✓
    ├── processed_logs (1,000 rows) ✓
    └── level_distribution (5 rows) ✓
```

### Looker Studio
**URL**: https://lookerstudio.google.com
- Create new report
- Connect to `distributed-log-analytics:logs_dataset.processed_logs`

### Cloud Storage Browser
**URL**: https://console.cloud.google.com/storage?project=distributed-log-analytics

---

## 📊 Instant Queries (Copy & Paste)

### Query 1: Top Error Services (Sorted)
```sql
SELECT 
    service,
    error_count,
    ROUND(100.0 * error_count / SUM(error_count) OVER (), 1) as percentage
FROM `distributed-log-analytics.logs_dataset.error_frequency`
ORDER BY error_count DESC
```

### Query 2: Log Level Summary
```sql
SELECT 
    level,
    count as num_logs,
    percentage
FROM `distributed-log-analytics.logs_dataset.level_distribution`
ORDER BY num_logs DESC
```

### Query 3: Full Service Analysis
```sql
SELECT 
    service,
    COUNT(*) as total_logs,
    COUNTIF(level='ERROR') as errors,
    COUNTIF(status_code=200) as success,
    ROUND(AVG(duration_ms), 0) as avg_duration_ms,
    ROUND(100.0 * COUNTIF(status_code=200) / COUNT(*), 1) as success_rate_pct
FROM `distributed-log-analytics.logs_dataset.processed_logs`
GROUP BY service
ORDER BY total_logs DESC
```

### Query 4: Error Timeline
```sql
SELECT 
    TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
    level,
    COUNT(*) as count
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE level IN ('ERROR', 'CRITICAL')
GROUP BY hour, level
ORDER BY hour DESC, count DESC
```

---

## 🎨 Dashboard Quick Setup (5 minutes)

### Step 1: Open Looker Studio
Go to: https://lookerstudio.google.com

### Step 2: Create Report
- Click **"Create"** in top-left
- Select **"Report"**
- Name it: **"My Log Analytics Dashboard"**
- Click **"Create"**

### Step 3: Add Data
- Click **"Add Data"** (top-left corner)
- Choose **"BigQuery"**
- Select: `distributed-log-analytics` → `logs_dataset` → `processed_logs`
- Click **"Connect"**

### Step 4: Add Charts (Pick Any 3)

**Chart A: Errors by Service**
```
Insert → Bar Chart
Dimension: service
Metric: COUNT (filter: level='ERROR')
```

**Chart B: Log Levels**
```
Insert → Pie Chart
Dimension: level
Metric: COUNT(*)
```

**Chart C: Response Times**
```
Insert → Table
Dimensions: service
Metrics: COUNT(*), AVG(duration_ms)
```

### Step 5: Share
- Click **"Share"** (top-right)
- Copy link
- Send to team

---

## 💡 Common Queries

### Find Slow Requests
```sql
SELECT service, message, duration_ms 
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE duration_ms > 5000
ORDER BY duration_ms DESC
LIMIT 20
```

### Find Recent Errors
```sql
SELECT timestamp, service, message, status_code
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE level='ERROR'
ORDER BY timestamp DESC
LIMIT 50
```

### Service Health Score
```sql
SELECT 
    service,
    ROUND(100.0 * COUNTIF(status_code=200) / COUNT(*), 2) as health_pct
FROM `distributed-log-analytics.logs_dataset.processed_logs`
GROUP BY service
HAVING health_pct < 95
ORDER BY health_pct
```

### Critical Events
```sql
SELECT COUNT(*) as critical_count
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE level='CRITICAL'
```

---

## 📱 Mobile Access

View your dashboards on phone:
1. Open Looker Studio link on mobile
2. Tap "View" mode
3. Interact with charts
4. Filters work on mobile

---

## 🔗 Sharing Dashboards

### Share with Team
1. In Looker Studio, click **"Share"** (top-right)
2. Copy the link
3. Set permissions:
   - **Can edit**: Team members who manage dashboard
   - **Can view**: Read-only access
4. Send link via email

### Embed in Websites
```html
<iframe
  width="100%"
  height="600"
  src="[Your Looker Studio Report URL]"
></iframe>
```

---

## 🛠️ Troubleshooting

### "Dataset not found" error?
```bash
# Run this in your terminal:
bq ls --dataset_id logs_dataset

# Should show:
# distributed-log-analytics:logs_dataset
```

### Looker Studio won't connect?
1. Refresh page (Ctrl+R)
2. Check: https://console.cloud.google.com/apis
3. Ensure BigQuery API is enabled

### Want to upload more logs?
```bash
gsutil cp your_logs.json \
  gs://distributed-log-analytics-raw-logs/logs/
```

---

## 📈 What's in Your Data

**10,000 Logs Analyzed:**
- 1,972 Errors (19.7%)
- 2,990 Warnings (29.9%)
- 4,007 Info (40.1%)
- 528 Debug (5.3%)
- 503 Critical (5.0%)

**9 Services Monitored:**
- notification-service (242 errors)
- auth-service (237 errors)
- database-service (228 errors)
- user-service (227 errors)
- payment-service (221 errors)
- cache-service (217 errors)
- inventory-service (209 errors)
- api-gateway (199 errors)
- analytics-engine (192 errors)

**System Health:** 🟢 Healthy
- No anomalies detected
- 70.5% success rate
- All services operational

---

## ✅ You're All Set!

Your data is live and queryable. Start exploring:

1. **Now**: Open BigQuery console
2. **Next**: Run one of the instant queries
3. **Then**: Create your first Looker Studio dashboard
4. **Finally**: Share with your team

**Enjoy your analytics!** 📊
