-- BigQuery SQL Queries for Distributed Log Analytics
-- These queries analyze processed batch analytics results

-- 1. Top 10 Services with Most Errors (All-Time)
SELECT 
    service, 
    error_count,
    ROUND(100.0 * error_count / SUM(error_count) OVER (), 2) as error_percentage
FROM 
    `your-project-id.logs_dataset.error_frequency`
ORDER BY 
    error_count DESC
LIMIT 10;

-- 2. Log Level Distribution Analysis
SELECT 
    level,
    count as log_count,
    ROUND(100.0 * count / SUM(count) OVER (), 2) as percentage
FROM 
    `your-project-id.logs_dataset.level_distribution`
ORDER BY 
    log_count DESC;

-- 3. Component Failure Analysis (Most Failed Components)
SELECT 
    component,
    failure_count,
    RANK() OVER (ORDER BY failure_count DESC) as failure_rank
FROM 
    `your-project-id.logs_dataset.component_failures`
WHERE 
    component IS NOT NULL AND component != ""
LIMIT 20;

-- 4. Hourly Error Trend Analysis
SELECT 
    hour,
    hourly_errors,
    AVG(hourly_errors) OVER (ORDER BY hour ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) as moving_avg
FROM 
    `your-project-id.logs_dataset.temporal_analysis`
ORDER BY 
    hour;

-- 5. Anomaly Detection Results
SELECT 
    service,
    error_count,
    status,
    severity,
    CURRENT_TIMESTAMP() as detected_at
FROM 
    `your-project-id.logs_dataset.anomalies`
WHERE 
    status = 'ANOMALY_DETECTED'
ORDER BY 
    severity DESC, error_count DESC;

-- 6. Critical and High Severity Errors by Service
SELECT 
    service,
    COUNT(*) as critical_count,
    MIN(timestamp) as first_occurrence,
    MAX(timestamp) as last_occurrence
FROM 
    `your-project-id.logs_dataset.processed_logs`
WHERE 
    level IN ('ERROR', 'CRITICAL')
GROUP BY 
    service
ORDER BY 
    critical_count DESC;

-- 7. Error Pattern Analysis (Most Common Error Messages)
SELECT 
    message,
    COUNT(*) as occurrence_count,
    COUNT(DISTINCT service) as affected_services
FROM 
    `your-project-id.logs_dataset.processed_logs`
WHERE 
    level = 'ERROR'
GROUP BY 
    message
ORDER BY 
    occurrence_count DESC
LIMIT 15;

-- 8. Service Health Summary
SELECT 
    service,
    COUNT(*) as total_logs,
    COUNTIF(level = 'ERROR') as error_count,
    COUNTIF(level = 'CRITICAL') as critical_count,
    ROUND(100.0 * COUNTIF(level = 'ERROR') / COUNT(*), 2) as error_rate_percent
FROM 
    `your-project-id.logs_dataset.processed_logs`
GROUP BY 
    service
ORDER BY 
    error_rate_percent DESC;
