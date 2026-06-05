# Using Google Cloud Platform Tools for Log Analytics

## 📊 Your Pipeline Results Summary

**Successfully Processed:**
- ✅ 10,000 logs generated and processed
- ✅ Log distribution: INFO (40.1%), WARNING (29.9%), ERROR (19.7%), DEBUG (5.3%), CRITICAL (5.0%)
- ✅ 9 microservices analyzed
- ✅ Anomaly detection performed (0 anomalies detected - system healthy!)

---

## 1️⃣ BigQuery Console - Query and Analyze Data

### Step-by-Step Guide

#### A. Access BigQuery
1. Go to: https://console.cloud.google.com/bigquery
2. Sign in with your Google account
3. Select project: `distributed-log-analytics`

#### B. Navigate to Your Data
In the left sidebar:
```
distributed-log-analytics (your project)
├── logs_dataset
│   ├── error_frequency
│   ├── processed_logs  ← Your data is here
│   └── anomalies
```

#### C. Sample SQL Queries

**Query 1: View recent logs**
```sql
SELECT 
    timestamp,
    level,
    service,
    message,
    duration_ms,
    status_code
FROM `distributed-log-analytics.logs_dataset.processed_logs`
LIMIT 20
```

**Query 2: Error analysis by service**
```sql
SELECT 
    service,
    COUNT(*) as error_count,
    AVG(duration_ms) as avg_response_time_ms,
    MAX(duration_ms) as max_response_time_ms
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE level = 'ERROR'
GROUP BY service
ORDER BY error_count DESC
```

**Query 3: Log level distribution**
```sql
SELECT 
    level,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) as percentage
FROM `distributed-log-analytics.logs_dataset.processed_logs`
GROUP BY level
ORDER BY count DESC
```

**Query 4: HTTP status code analysis**
```sql
SELECT 
    status_code,
    COUNT(*) as count,
    ROUND(AVG(duration_ms), 2) as avg_duration_ms,
    COUNTIF(level = 'ERROR') as error_count
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE status_code > 0
GROUP BY status_code
ORDER BY count DESC
```

**Query 5: Service performance comparison**
```sql
SELECT 
    service,
    COUNT(*) as total_requests,
    COUNTIF(level = 'ERROR') as errors,
    COUNTIF(status_code = 200) as successful_requests,
    ROUND(AVG(duration_ms), 2) as avg_response_time_ms,
    ROUND(100.0 * COUNTIF(status_code = 200) / COUNT(*), 2) as success_rate_pct
FROM `distributed-log-analytics.logs_dataset.processed_logs`
GROUP BY service
ORDER BY total_requests DESC
```

### How to Run Queries in BigQuery Console

1. Click "**+ Compose New Query**" button
2. Paste SQL query in the editor
3. Click "**Run**" or press Ctrl+Enter
4. Results appear below with options to:
   - **Save**: Save query for later
   - **Explore Data**: Visualize with charts
   - **Download**: Export as CSV

### Query Performance Tips
- Use `WHERE` clauses to filter data
- `LIMIT` results to avoid large downloads
- Use `DATE()` functions for time-based filtering
- Check execution time in bottom-right corner

---

## 2️⃣ Looker Studio - Create Visualizations

### Step 1: Create a New Report
1. Go to: https://lookerstudio.google.com
2. Click "**Create**" → "**Report**"
3. Give it a name: "Log Analytics Dashboard"
4. Click "**Create**"

### Step 2: Add Data Source
1. Click "**Create New Data Source**"
2. Select "**BigQuery**"
3. Choose your project: `distributed-log-analytics`
4. Select dataset: `logs_dataset`
5. Select table: `processed_logs`
6. Click "**Connect**"

### Step 3: Add Charts and Visualizations

#### Chart 1: Log Level Distribution (Pie Chart)
```
Chart Type: Pie Chart
Dimension: level
Metric: Count
Dimension Color: level
```

#### Chart 2: Errors by Service (Bar Chart)
```
Chart Type: Bar Chart
Dimension: service
Metric: COUNT(CASE WHEN level = 'ERROR' THEN 1 END)
Sort: Metric descending
```

#### Chart 3: Response Time Trend (Time Series)
```
Chart Type: Time Series Chart
Dimension: timestamp (set to hourly)
Metric: AVG(duration_ms)
Breakdown: service
```

#### Chart 4: Service Status Overview (Scorecard)
```
Chart Type: Scorecard
Metric 1: COUNT(*) → Label "Total Logs"
Metric 2: COUNTIF(level='ERROR') → Label "Total Errors"
Metric 3: COUNTIF(status_code=200) → Label "Successful Requests"
```

#### Chart 5: Status Code Distribution (Donut Chart)
```
Chart Type: Donut Chart
Dimension: status_code
Metric: Count
```

### Step 4: Add Filters and Interactivity
1. Click "**Add a filter**" button
2. Add Date Range filter:
   - Field: `timestamp`
   - Type: Date Range
3. Add Service filter:
   - Field: `service`
   - Type: Dropdown

### Step 5: Customize Layout
- Drag charts to rearrange
- Resize by dragging corner
- Click chart to edit colors, fonts, titles
- Add text boxes for descriptions

### Step 6: Share Your Dashboard
1. Click "**Share**" button (top right)
2. Get shareable link
3. Set permissions:
   - **Editor**: Can edit
   - **Viewer**: Can only view
   - **Viewer (with link)**: Anyone with link can view

---

## 3️⃣ Key Metrics to Monitor

### From Your Data Analysis:

**Log Distribution:**
- INFO: 4,007 logs (40.1%)
- WARNING: 2,990 logs (29.9%)
- ERROR: 1,972 logs (19.7%)
- DEBUG: 528 logs (5.3%)
- CRITICAL: 503 logs (5.0%)

**Service Analysis:**
- Most Errors: notification-service (242)
- Most Warnings: payment-service (353)
- Average Response Time: 2,436-2,559 ms across services

**HTTP Status Codes:**
- 200 OK: 7,047 (70.5%) ✅ Healthy
- 400 Bad Request: 989 (9.9%)
- 201 Created: 988 (9.9%)
- 500 Server Error: 497 (5.0%)
- 401 Unauthorized: 479 (4.8%)

**Anomaly Detection Result:**
- ✅ All services operating within normal range
- No alerts triggered
- System health: NORMAL

---

## 4️⃣ Advanced BigQuery Features

### Creating Saved Queries
1. Run a query
2. Click "**Save Query**"
3. Name it (e.g., "Error Analysis")
4. Access from left sidebar later

### Creating Views (Virtual Tables)
```sql
CREATE VIEW logs_dataset.error_summary AS
SELECT 
    DATE(timestamp) as date,
    service,
    COUNT(*) as error_count,
    AVG(duration_ms) as avg_duration
FROM `distributed-log-analytics.logs_dataset.processed_logs`
WHERE level = 'ERROR'
GROUP BY date, service
```

### Scheduled Queries (Automated Reports)
1. Write query
2. Click "**Schedule Query**"
3. Set frequency (daily, hourly, etc.)
4. Results auto-save to new table

### Setting Alerts
1. In Looker Studio report
2. Click report settings
3. Set up alerts for:
   - Error count exceeds threshold
   - Response time > 5000ms
   - Specific service failures

---

## 5️⃣ Connecting to Other Tools

### Export to Sheets
```
Looker Studio → Chart → Click ⋮ → Export → Google Sheets
```

### Export to CSV
```
BigQuery → Query Results → Download → CSV
```

### API Access
```python
from google.cloud import bigquery

client = bigquery.Client(project='distributed-log-analytics')
query = """
    SELECT * FROM `distributed-log-analytics.logs_dataset.processed_logs`
    WHERE level = 'ERROR' LIMIT 100
"""
results = client.query(query).result()
df = results.to_dataframe()
```

---

## 🎯 Next Steps

1. **Today:**
   - ✅ View data in BigQuery Console
   - ✅ Run sample queries
   - ✅ Create first dashboard in Looker

2. **This Week:**
   - Set up automated anomaly alerts
   - Create department-specific dashboards
   - Schedule daily reports

3. **Ongoing:**
   - Monitor error trends
   - Optimize slow services (inventory-service at 2,554ms avg)
   - Track payment-service warnings (353 count)

---

## 📞 Quick Reference

| Tool | URL | Purpose |
|------|-----|---------|
| BigQuery | https://console.cloud.google.com/bigquery | Query and analyze data |
| Looker Studio | https://lookerstudio.google.com | Create visualizations & dashboards |
| Cloud Console | https://console.cloud.google.com | Manage GCP resources |
| Cloud Storage | https://console.cloud.google.com/storage | View uploaded logs |

---

## ✅ Your System Is Ready!

Your distributed log analytics system is now fully operational with:
- ✅ 10,000 logs processed
- ✅ Analytics computed
- ✅ Anomalies detected
- ✅ Ready for visualization

**Start exploring your data in BigQuery and build your dashboards in Looker Studio!**
