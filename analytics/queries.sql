-- BigQuery SQL Queries for Log Analytics

-- 1. Get Top 10 Services with Most Errors Today
SELECT 
    service, 
    COUNT(*) as error_count
FROM 
    `your-project-id.logs_dataset.error_logs`
WHERE 
    DATE(timestamp) = CURRENT_DATE()
GROUP BY 
    service
ORDER BY 
    error_count DESC
LIMIT 10;

-- 2. Error Trend Analysis (Grouped by hour)
SELECT 
    TIMESTAMP_TRUNC(timestamp, HOUR) as hour_bucket,
    COUNT(*) as total_errors
FROM 
    `your-project-id.logs_dataset.error_logs`
WHERE 
    timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY 
    hour_bucket
ORDER BY 
    hour_bucket ASC;

-- 3. Detailed Trace for Specific Service failures
SELECT 
    timestamp, 
    message, 
    trace_id
FROM 
    `your-project-id.logs_dataset.error_logs`
WHERE 
    service = 'payment-gateway'
ORDER BY 
    timestamp DESC
LIMIT 100;
