"""
Log Processing and Analytics (without external dependencies)
Shows analytics results that would be uploaded to BigQuery
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Configuration
PROJECT_ID = "distributed-log-analytics"
DATASET_ID = "logs_dataset"
TABLE_ID = "processed_logs"

class SimpleLogProcessor:
    """Process logs and display analytics"""
    
    def __init__(self):
        self.processed_logs = []
        self.statistics = defaultdict(int)
    
    def load_local_logs(self, local_path="data/sample_logs.json"):
        """Load logs from local file"""
        print(f"Loading logs from: {local_path}")
        
        logs = []
        with open(local_path, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line)
                    logs.append(log)
                except json.JSONDecodeError:
                    continue
        
        print(f"✓ Loaded {len(logs)} logs")
        return logs
    
    def process_logs(self, logs):
        """
        Process raw logs: parsing, cleaning, feature extraction
        """
        print("\n" + "="*70)
        print("STAGE 1: LOG PROCESSING & FEATURE EXTRACTION")
        print("="*70)
        
        processed = []
        
        for i, log in enumerate(logs):
            try:
                # Extract and clean features
                processed_log = {
                    'timestamp': log.get('timestamp', datetime.utcnow().isoformat()),
                    'level': log.get('level', 'INFO').upper(),
                    'service': log.get('service', 'unknown'),
                    'node': log.get('node', 'unknown'),
                    'message': str(log.get('message', ''))[:100],  # Truncate long messages
                    'request_id': log.get('request_id', ''),
                    'duration_ms': int(log.get('duration_ms', 0)),
                    'status_code': int(log.get('status_code', 0)),
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                processed.append(processed_log)
                
                # Collect statistics
                self.statistics[f"level_{processed_log['level']}"] += 1
                self.statistics[f"service_{processed_log['service']}"] += 1
                
                if i < 3:
                    print(f"  Sample log {i+1}: {processed_log['level']} - {processed_log['message'][:50]}")
                
            except Exception as e:
                continue
        
        print(f"\n✓ Successfully processed {len(processed)} logs")
        
        # Print statistics
        print(f"\n{'='*70}")
        print("Log Level Distribution:")
        print(f"{'='*70}")
        for key, count in sorted(self.statistics.items()):
            if key.startswith('level_'):
                level = key.replace('level_', '')
                pct = 100 * count / len(processed)
                print(f"  {level:<12}: {count:>6} ({pct:>5.1f}%)")
        
        return processed
    
    def perform_analytics(self, logs):
        """Perform batch analytics on processed logs"""
        print(f"\n{'='*70}")
        print("STAGE 2: BATCH ANALYTICS")
        print(f"{'='*70}")
        
        # Aggregate statistics
        error_by_service = Counter()
        warning_by_service = Counter()
        info_by_service = Counter()
        status_codes = Counter()
        avg_duration = defaultdict(list)
        
        for log in logs:
            if log['level'] == 'ERROR':
                error_by_service[log['service']] += 1
            elif log['level'] == 'WARNING':
                warning_by_service[log['service']] += 1
            elif log['level'] == 'INFO':
                info_by_service[log['service']] += 1
            
            status_codes[log['status_code']] += 1
            
            if log['duration_ms'] > 0:
                avg_duration[log['service']].append(log['duration_ms'])
        
        print(f"\nTop 5 services by ERROR count:")
        print(f"{'Service':<25} {'Errors':<10}")
        print("-" * 35)
        for service, count in error_by_service.most_common(5):
            print(f"  {service:<23} {count:<10}")
        
        print(f"\nTop 5 services by WARNING count:")
        print(f"{'Service':<25} {'Warnings':<10}")
        print("-" * 35)
        for service, count in warning_by_service.most_common(5):
            print(f"  {service:<23} {count:<10}")
        
        print(f"\nHTTP Status Code Distribution:")
        print(f"{'Status':<10} {'Count':<10} {'Percentage':<10}")
        print("-" * 30)
        for status, count in sorted(status_codes.items(), key=lambda x: -x[1])[:5]:
            pct = 100 * count / len(logs)
            print(f"  {status:<8} {count:<10} {pct:<8.1f}%")
        
        print(f"\nAverage Response Time by Service:")
        print(f"{'Service':<25} {'Avg (ms)':<10} {'Count':<10}")
        print("-" * 45)
        for service, durations in sorted(avg_duration.items()):
            if durations:
                avg = sum(durations) / len(durations)
                print(f"  {service:<23} {avg:<8.2f} {len(durations):<10}")
        
        return {
            'error_by_service': dict(error_by_service),
            'warning_by_service': dict(warning_by_service),
            'status_codes': dict(status_codes)
        }
    
    def detect_anomalies(self, logs):
        """Simple anomaly detection"""
        print(f"\n{'='*70}")
        print("STAGE 3: ANOMALY DETECTION")
        print(f"{'='*70}")
        
        # Calculate baselines
        error_counts = Counter(log['service'] for log in logs if log['level'] == 'ERROR')
        
        if error_counts:
            avg_errors = sum(error_counts.values()) / len(error_counts)
            std_dev = (sum((x - avg_errors) ** 2 for x in error_counts.values()) / len(error_counts)) ** 0.5
            threshold = avg_errors + (2 * std_dev)  # 2-sigma threshold
            
            print(f"\nError Rate Analysis:")
            print(f"  Average errors per service: {avg_errors:.1f}")
            print(f"  Standard deviation: {std_dev:.1f}")
            print(f"  Anomaly threshold (2-sigma): {threshold:.1f}")
            
            print(f"\nDetected Anomalies (services exceeding threshold):")
            print(f"{'Service':<25} {'Errors':<10} {'Status':<15}")
            print("-" * 50)
            
            anomalies = []
            for service, count in error_counts.most_common(10):
                if count > threshold:
                    status = "🔴 ANOMALY"
                    anomalies.append((service, count))
                else:
                    status = "✓ Normal"
                print(f"  {service:<23} {count:<10} {status:<15}")
            
            print(f"\n✓ Total anomalies detected: {len(anomalies)}")
            return anomalies
        
        return []

def main():
    print("\n" + "="*70)
    print("  DISTRIBUTED LOG ANALYTICS PIPELINE")
    print("="*70)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Table: {TABLE_ID}")
    
    processor = SimpleLogProcessor()
    
    try:
        # Step 1: Load logs
        logs = processor.load_local_logs()
        
        # Step 2: Process logs
        processed_logs = processor.process_logs(logs)
        
        # Step 3: Perform analytics
        analytics = processor.perform_analytics(processed_logs)
        
        # Step 4: Detect anomalies
        anomalies = processor.detect_anomalies(processed_logs)
        
        print(f"\n{'='*70}")
        print("✓ PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"\n✓ Processed {len(processed_logs)} logs")
        print(f"✓ Detected {len(anomalies)} anomalies")
        print(f"\nReady to upload to BigQuery and visualize in Looker Studio!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
