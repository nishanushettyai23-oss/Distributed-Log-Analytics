"""
Batch Anomaly Detection Module
Analyzes batch processing results from BigQuery to identify anomalies.
Uses statistical methods to detect unusual patterns and system behavior.
"""

from google.cloud import bigquery
import json
from datetime import datetime, timedelta
from statistics import mean, stdev

# Configuration
PROJECT_ID = "distributed-log-analytics"
DATASET_ID = "logs_dataset"
ALERT_WEBHOOK_URL = "https://us-central1-distributed-log-analytics.cloudfunctions.net/alert-function"

class AnomalyDetector:
    """
    Batch-based anomaly detection system.
    Analyzes historical log data to identify unusual patterns.
    """
    
    def __init__(self, project_id, dataset_id):
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.anomalies = []
    
    def get_error_statistics(self):
        """
        Retrieve error statistics from processed batch results.
        Calculates baseline metrics for anomaly detection.
        """
        print("Calculating error statistics...")
        
        query = f"""
            SELECT 
                service,
                error_count
            FROM `{self.project_id}.{self.dataset_id}.error_frequency`
            ORDER BY error_count DESC
        """
        
        try:
            results = self.client.query(query).result()
            data = [row for row in results]
            
            if len(data) == 0:
                print("No error data found.")
                return None
            
            # Extract error counts
            error_counts = [row.error_count for row in data]
            
            statistics = {
                'mean': mean(error_counts),
                'stdev': stdev(error_counts) if len(error_counts) > 1 else 0,
                'min': min(error_counts),
                'max': max(error_counts),
                'total_services': len(data)
            }
            
            print(f"Error Statistics:")
            print(f"  Mean errors per service: {statistics['mean']:.2f}")
            print(f"  Std Dev: {statistics['stdev']:.2f}")
            print(f"  Min: {statistics['min']}, Max: {statistics['max']}")
            
            return statistics, data
        
        except Exception as e:
            print(f"Error retrieving statistics: {e}")
            return None
    
    def detect_anomalies(self, threshold_multiplier=2.0):
        """
        Detect anomalies using statistical thresholding.
        If service error_count > mean + (stdev * threshold_multiplier), flag as anomaly.
        """
        print(f"\nDetecting anomalies (threshold: {threshold_multiplier}x std dev)...")
        
        stats_result = self.get_error_statistics()
        
        if stats_result is None:
            return []
        
        statistics, service_data = stats_result
        
        # Calculate anomaly threshold
        threshold = statistics['mean'] + (statistics['stdev'] * threshold_multiplier)
        
        print(f"Anomaly threshold: {threshold:.2f}")
        
        anomalies = []
        
        for row in service_data:
            service = row.service
            error_count = row.error_count
            
            if error_count > threshold:
                # Determine severity level
                if error_count > threshold * 2:
                    severity = 'CRITICAL'
                elif error_count > threshold * 1.5:
                    severity = 'HIGH'
                else:
                    severity = 'MEDIUM'
                
                anomaly = {
                    'service': service,
                    'error_count': error_count,
                    'threshold': threshold,
                    'severity': severity,
                    'deviation': ((error_count - statistics['mean']) / statistics['mean'] * 100),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                anomalies.append(anomaly)
                self.anomalies.append(anomaly)
        
        return anomalies
    
    def analyze_error_patterns(self):
        """
        Analyze error patterns to identify recurring issues.
        """
        print("\nAnalyzing error patterns...")
        
        query = f"""
            SELECT 
                message,
                COUNT(*) as occurrence_count,
                COUNT(DISTINCT service) as affected_services
            FROM `{self.project_id}.{self.dataset_id}.processed_logs`
            WHERE level = 'ERROR'
            GROUP BY message
            ORDER BY occurrence_count DESC
            LIMIT 10
        """
        
        try:
            results = self.client.query(query).result()
            
            print("\nTop Error Patterns:")
            for row in results:
                print(f"  '{row.message}'")
                print(f"    - Occurrences: {row.occurrence_count}")
                print(f"    - Affected Services: {row.affected_services}")
            
            return list(results)
        
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return []
    
    def analyze_service_health(self):
        """
        Comprehensive service health analysis.
        Calculates error rates and identifies unhealthy services.
        """
        print("\nAnalyzing service health...")
        
        query = f"""
            SELECT 
                service,
                COUNT(*) as total_logs,
                COUNTIF(level = 'ERROR') as error_count,
                COUNTIF(level = 'CRITICAL') as critical_count,
                ROUND(100.0 * COUNTIF(level = 'ERROR') / COUNT(*), 2) as error_rate_percent
            FROM `{self.project_id}.{self.dataset_id}.processed_logs`
            GROUP BY service
            ORDER BY error_rate_percent DESC
        """
        
        try:
            results = list(self.client.query(query).result())
            
            print("\nService Health Report:")
            print("Service | Total Logs | Errors | Critical | Error Rate %")
            print("-" * 70)
            
            for row in results:
                print(f"{row.service:30} | {row.total_logs:10} | {row.error_count:6} | {row.critical_count:8} | {row.error_rate_percent:6.2f}%")
            
            return results
        
        except Exception as e:
            print(f"Error analyzing service health: {e}")
            return []
    
    def trigger_alerts(self):
        """
        Trigger alerts for detected anomalies.
        """
        if not self.anomalies:
            print("\nNo anomalies to alert on.")
            return
        
        print(f"\nTriggering {len(self.anomalies)} alert(s)...")
        
        for anomaly in self.anomalies:
            payload = {
                'service': anomaly['service'],
                'error_count': anomaly['error_count'],
                'severity': anomaly['severity'],
                'deviation_percent': f"{anomaly['deviation']:.2f}%",
                'timestamp': anomaly['timestamp'],
                'message': f"ANOMALY DETECTED: {anomaly['service']} has {anomaly['error_count']:.0f} errors ({anomaly['severity']} severity)"
            }
            
            print(f"\n  [{anomaly['severity']}] {anomaly['service']}")
            print(f"    Error Count: {anomaly['error_count']:.0f}")
            print(f"    Deviation: +{anomaly['deviation']:.1f}%")
            
            # In production, call webhook
            # self._send_alert(payload)
    
    def _send_alert(self, payload):
        """Send alert to external service (e.g., PagerDuty, Slack)."""
        try:
            import requests
            response = requests.post(ALERT_WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
            print(f"    ✓ Alert sent")
        except Exception as e:
            print(f"    ✗ Failed to send alert: {e}")
    
    def run_analysis(self):
        """Execute complete anomaly detection workflow."""
        print("=" * 70)
        print("BATCH ANOMALY DETECTION ANALYSIS")
        print("=" * 70)
        
        # Run all analyses
        self.detect_anomalies(threshold_multiplier=2.0)
        self.analyze_error_patterns()
        self.analyze_service_health()
        self.trigger_alerts()
        
        print("\n" + "=" * 70)
        print(f"ANALYSIS COMPLETE - {len(self.anomalies)} anomalies detected")
        print("=" * 70)

def main():
    """Main entry point for anomaly detection."""
    detector = AnomalyDetector(PROJECT_ID, DATASET_ID)
    detector.run_analysis()

if __name__ == "__main__":
    main()
