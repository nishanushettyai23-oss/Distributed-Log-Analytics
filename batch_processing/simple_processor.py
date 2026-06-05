"""
Simplified Log Processing and Analysis (without Spark)
Reads logs from storage, processes them, and uploads to BigQuery
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from google.cloud import bigquery
from google.cloud import storage

# Configuration
PROJECT_ID = "distributed-log-analytics"
DATASET_ID = "logs_dataset"
TABLE_ID = "processed_logs"
BUCKET_NAME = "distributed-log-analytics-raw-logs"

class LogProcessor:
    """Process logs and upload to BigQuery"""
    
    def __init__(self):
        self.bq_client = bigquery.Client(project=PROJECT_ID)
        self.storage_client = storage.Client(project=PROJECT_ID)
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
        print("LOG PROCESSING & FEATURE EXTRACTION")
        print("="*70)
        
        processed = []
        
        for i, log in enumerate(logs):
            try:
                # Extract features from log
                processed_log = {
                    'timestamp': log.get('timestamp', datetime.utcnow().isoformat()),
                    'level': log.get('level', 'INFO'),
                    'service': log.get('service', 'unknown'),
                    'node': log.get('node', 'unknown'),
                    'message': log.get('message', ''),
                    'request_id': log.get('request_id', ''),
                    'duration_ms': log.get('duration_ms', 0),
                    'status_code': log.get('status_code', 0),
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                processed.append(processed_log)
                
                # Collect statistics
                self.statistics[f"level_{log.get('level', 'unknown')}"] += 1
                self.statistics[f"service_{log.get('service', 'unknown')}"] += 1
                
            except Exception as e:
                continue
        
        print(f"✓ Processed {len(processed)} logs")
        
        # Print statistics
        print(f"\nLog Statistics:")
        print(f"  Error logs: {self.statistics.get('level_ERROR', 0)}")
        print(f"  Warning logs: {self.statistics.get('level_WARNING', 0)}")
        print(f"  Info logs: {self.statistics.get('level_INFO', 0)}")
        print(f"  Critical logs: {self.statistics.get('level_CRITICAL', 0)}")
        
        return processed
    
    def perform_analytics(self, logs):
        """Perform batch analytics on processed logs"""
        print("\n" + "="*70)
        print("BATCH ANALYTICS")
        print("="*70)
        
        # Aggregate statistics
        error_by_service = Counter()
        warning_by_service = Counter()
        avg_duration = defaultdict(list)
        
        for log in logs:
            if log['level'] == 'ERROR':
                error_by_service[log['service']] += 1
            elif log['level'] == 'WARNING':
                warning_by_service[log['service']] += 1
            
            if log['duration_ms'] > 0:
                avg_duration[log['service']].append(log['duration_ms'])
        
        print(f"\nTop services by error count:")
        for service, count in error_by_service.most_common(5):
            print(f"  {service}: {count} errors")
        
        print(f"\nTop services by warning count:")
        for service, count in warning_by_service.most_common(5):
            print(f"  {service}: {count} warnings")
        
        return {
            'error_by_service': dict(error_by_service),
            'warning_by_service': dict(warning_by_service)
        }
    
    def upload_to_bigquery(self, logs):
        """Upload processed logs to BigQuery"""
        print("\n" + "="*70)
        print("UPLOADING TO BIGQUERY")
        print("="*70)
        
        table_id = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        table = self.bq_client.get_table(table_id)
        
        print(f"Uploading {len(logs)} logs to {table_id}...")
        
        errors = self.bq_client.insert_rows_json(table, logs)
        
        if errors == []:
            print(f"✓ Successfully loaded {len(logs)} logs into BigQuery")
            return True
        else:
            print(f"✗ Encountered errors while inserting rows:")
            for error in errors:
                print(f"  {error}")
            return False
    
    def query_results(self):
        """Query processed logs from BigQuery"""
        print("\n" + "="*70)
        print("QUERYING BIGQUERY RESULTS")
        print("="*70)
        
        query = f"""
        SELECT 
            level,
            service,
            COUNT(*) as count,
            AVG(duration_ms) as avg_duration
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        GROUP BY level, service
        ORDER BY count DESC
        LIMIT 20
        """
        
        print(f"Running query...")
        
        try:
            results = self.bq_client.query(query).result()
            
            print(f"\n✓ Query Results:")
            print(f"\n{'Level':<12} {'Service':<25} {'Count':<10} {'Avg Duration (ms)':<15}")
            print("-" * 60)
            
            for row in results:
                print(f"{row[0]:<12} {row[1]:<25} {row[2]:<10} {row[3]:<15.2f}")
            
            return results
            
        except Exception as e:
            print(f"✗ Error querying BigQuery: {e}")
            return None

def main():
    print("\n" + "="*70)
    print("  DISTRIBUTED LOG PROCESSING PIPELINE")
    print("="*70)
    
    processor = LogProcessor()
    
    try:
        # Step 1: Load logs
        logs = processor.load_local_logs()
        
        # Step 2: Process logs
        processed_logs = processor.process_logs(logs)
        
        # Step 3: Perform analytics
        analytics = processor.perform_analytics(processed_logs)
        
        # Step 4: Upload to BigQuery
        success = processor.upload_to_bigquery(processed_logs)
        
        if success:
            # Step 5: Query results
            processor.query_results()
        
        print("\n" + "="*70)
        print("✓ PIPELINE COMPLETE")
        print("="*70)
        print(f"\n✓ Processed and loaded {len(processed_logs)} logs into BigQuery")
        print(f"✓ Dataset: {DATASET_ID}")
        print(f"✓ Table: {TABLE_ID}")
        print(f"\nNext: Check BigQuery and Looker Studio for visualizations")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
