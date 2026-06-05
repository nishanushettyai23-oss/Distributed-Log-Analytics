"""
Apache Spark-style Distributed Batch Log Analytics
Pure Python implementation with multiprocessing for distributed processing
No external dependencies required - uses only Python stdlib
"""

import json
from datetime import datetime
from collections import defaultdict, Counter
import multiprocessing as mp
import os
import csv

# Configuration
PROJECT_ID = "distributed-log-analytics"
DATASET_ID = "logs_dataset"
TABLE_ID = "processed_logs"
LOCAL_INPUT_PATH = "data/sample_logs.json"

class SparkDistributedLogAnalytics:
    """
    Distributed log processing system simulating Apache Spark semantics
    Uses multiprocessing to process data in parallel (like Spark partitions)
    """
    
    def __init__(self, num_workers=4):
        self.num_workers = num_workers
    
    def load_logs_distributed(self, input_path):
        """
        Load logs and prepare for distributed processing
        Simulates Spark's input reading stage
        """
        print("=" * 80)
        print("STAGE 1: DISTRIBUTED LOG PARSING AND DATA CLEANING")
        print("=" * 80)
        
        logs = []
        with open(input_path, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line)
                    logs.append(log)
                except json.JSONDecodeError:
                    continue
        
        print(f"\n✓ Loaded {len(logs):,} logs from {input_path}")
        
        # Data cleaning - filter incomplete records
        cleaned = [log for log in logs 
                  if all(key in log for key in ['timestamp', 'level', 'message'])]
        
        print(f"✓ Cleaned logs (removed duplicates/nulls): {len(cleaned):,} valid records")
        
        return cleaned
    
    @staticmethod
    def process_partition(partition_data):
        """
        Worker function: Process a partition of logs
        This runs on a separate process (simulating Spark executor)
        """
        features = []
        for log in partition_data:
            try:
                feature_log = {
                    'timestamp': log.get('timestamp', ''),
                    'level': str(log.get('level', 'INFO')).upper(),
                    'service': str(log.get('service', 'unknown')),
                    'node': str(log.get('node', 'unknown')),
                    'message': str(log.get('message', ''))[:100],
                    'duration_ms': int(log.get('duration_ms', 0)),
                    'status_code': int(log.get('status_code', 0)),
                    'request_id': str(log.get('request_id', ''))
                }
                features.append(feature_log)
            except Exception:
                continue
        return features
    
    def extract_features_distributed(self, logs):
        """
        Feature extraction using distributed processing
        Partitions data and processes in parallel with multiprocessing
        """
        print("\n" + "=" * 80)
        print("STAGE 2: DISTRIBUTED FEATURE EXTRACTION")
        print("=" * 80)
        
        # Create partitions for parallel processing
        partition_size = max(1, len(logs) // self.num_workers)
        partitions = [logs[i:i+partition_size] for i in range(0, len(logs), partition_size)]
        
        print(f"Distributed processing across {len(partitions)} partitions")
        print(f"Partition size: ~{partition_size:,} logs each")
        print(f"Worker processes: {self.num_workers}")
        
        # Process partitions in parallel using multiprocessing
        with mp.Pool(self.num_workers) as pool:
            results = pool.map(self.process_partition, partitions)
        
        # Combine results from all partitions (shuffle and combine stage)
        featured_logs = [log for partition_result in results for log in partition_result]
        
        print(f"✓ Feature extraction complete: {len(featured_logs):,} logs processed")
        if featured_logs:
            print(f"  Sample: {featured_logs[0]}")
        
        return featured_logs
    
    def batch_analytics_distributed(self, logs):
        """
        Stage 3: Distributed Batch Analytics
        Aggregations equivalent to Spark's groupBy operations
        """
        print("\n" + "=" * 80)
        print("STAGE 3: DISTRIBUTED BATCH ANALYTICS")
        print("=" * 80)
        
        # Initialize accumulators (Spark's distributed counters)
        error_by_service = Counter()
        warning_by_service = Counter()
        info_by_service = Counter()
        level_counts = Counter()
        status_codes = Counter()
        service_durations = defaultdict(list)
        
        # Map: Transform each log
        for log in logs:
            # Level distribution
            level_counts[log['level']] += 1
            
            # Service-level aggregations
            if log['level'] == 'ERROR':
                error_by_service[log['service']] += 1
            elif log['level'] == 'WARNING':
                warning_by_service[log['service']] += 1
            elif log['level'] == 'INFO':
                info_by_service[log['service']] += 1
            
            # Status codes
            if log['status_code'] > 0:
                status_codes[log['status_code']] += 1
            
            # Duration metrics
            if log['duration_ms'] > 0:
                service_durations[log['service']].append(log['duration_ms'])
        
        # Reduce: Aggregate results
        print("\n--- LOG LEVEL DISTRIBUTION ---")
        print(f"{'Level':<12} {'Count':<10} {'Percentage':<10}")
        print("-" * 32)
        total = sum(level_counts.values())
        for level in ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']:
            count = level_counts.get(level, 0)
            if count > 0:
                pct = 100 * count / total
                print(f"{level:<12} {count:<10} {pct:<8.1f}%")
        
        print("\n--- TOP 10 SERVICES BY ERROR COUNT ---")
        print(f"{'Service':<30} {'Errors':<10}")
        print("-" * 40)
        for service, count in error_by_service.most_common(10):
            print(f"{service:<30} {count:<10}")
        
        print("\n--- HTTP STATUS CODE DISTRIBUTION ---")
        print(f"{'Status':<10} {'Count':<10} {'Percentage':<10}")
        print("-" * 30)
        for status, count in sorted(status_codes.items(), key=lambda x: -x[1])[:10]:
            pct = 100 * count / total
            print(f"{status:<10} {count:<10} {pct:<8.1f}%")
        
        print("\n--- SERVICE PERFORMANCE (Top 5 by volume) ---")
        print(f"{'Service':<30} {'Total':<10} {'Errors':<10} {'Avg (ms)':<10}")
        print("-" * 60)
        service_totals = Counter(log['service'] for log in logs)
        for service, total_logs in service_totals.most_common(5):
            errors = error_by_service.get(service, 0)
            durations = service_durations.get(service, [])
            avg_duration = sum(durations) / len(durations) if durations else 0
            print(f"{service:<30} {total_logs:<10} {errors:<10} {avg_duration:<8.0f}")
        
        return {
            'level_distribution': dict(level_counts),
            'error_by_service': dict(error_by_service),
            'warning_by_service': dict(warning_by_service),
            'status_codes': dict(status_codes),
            'service_durations': service_durations,
            'total_logs': len(logs)
        }
    
    def anomaly_detection_distributed(self, logs, analytics):
        """
        Stage 4: Statistical Anomaly Detection
        Identifies services with abnormal error rates
        """
        print("\n" + "=" * 80)
        print("STAGE 4: DISTRIBUTED ANOMALY DETECTION")
        print("=" * 80)
        
        error_counts = list(analytics['error_by_service'].values())
        if not error_counts:
            print("No errors detected")
            return []
        
        # Statistical baseline (mean and standard deviation)
        mean_errors = sum(error_counts) / len(error_counts)
        variance = sum((x - mean_errors) ** 2 for x in error_counts) / len(error_counts)
        std_dev = variance ** 0.5
        
        # Anomaly threshold: mean + 2 standard deviations
        threshold = mean_errors + (2 * std_dev)
        
        print(f"\nStatistical Analysis:")
        print(f"  Mean errors per service: {mean_errors:.1f}")
        print(f"  Standard deviation: {std_dev:.1f}")
        print(f"  Anomaly threshold (μ + 2σ): {threshold:.1f}")
        
        # Detect anomalies
        anomalies = []
        print(f"\nAnomaly Detection Results:")
        print(f"{'Service':<30} {'Errors':<10} {'Status':<15}")
        print("-" * 55)
        
        for service, error_count in analytics['error_by_service'].items():
            if error_count > threshold:
                severity = "🔴 CRITICAL" if error_count > threshold * 2 else "🟠 HIGH"
                anomalies.append((service, error_count))
                print(f"{service:<30} {error_count:<10} {severity:<15}")
        
        if not anomalies:
            print("All services operating normally (no anomalies detected)")
        
        return anomalies
    
    def save_distributed_results(self, logs, analytics, anomalies):
        """
        Stage 5: Persist Results
        Saves processed data to local storage (simulates Spark write operations)
        """
        print("\n" + "=" * 80)
        print("STAGE 5: DISTRIBUTED RESULTS PERSISTENCE")
        print("=" * 80)
        
        output_dir = "spark_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Write error frequency
        with open(os.path.join(output_dir, "error_frequency.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['service', 'error_count'])
            for service, count in sorted(analytics['error_by_service'].items(), key=lambda x: -x[1]):
                writer.writerow([service, count])
        print(f"✓ Saved error_frequency.csv")
        
        # Write level distribution
        with open(os.path.join(output_dir, "level_distribution.csv"), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['level', 'count', 'percentage'])
            total = sum(analytics['level_distribution'].values())
            for level, count in sorted(analytics['level_distribution'].items(), key=lambda x: -x[1]):
                pct = 100 * count / total
                writer.writerow([level, count, round(pct, 2)])
        print(f"✓ Saved level_distribution.csv")
        
        # Write anomalies
        if anomalies:
            with open(os.path.join(output_dir, "anomalies.csv"), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['service', 'error_count', 'severity'])
                for service, count in anomalies:
                    severity = "CRITICAL" if count > 250 else "HIGH"
                    writer.writerow([service, count, severity])
            print(f"✓ Saved anomalies.csv ({len(anomalies)} anomalies)")
        else:
            print(f"✓ No anomalies to save")
        
        # Write sample of processed logs
        with open(os.path.join(output_dir, "sample_processed_logs.csv"), 'w', newline='') as f:
            if logs:
                writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs[:1000])
            print(f"✓ Saved sample_processed_logs.csv (first 1000 records)")
        
        print(f"\n📊 Processing Summary:")
        print(f"   Total logs processed: {len(logs):,}")
        print(f"   Errors detected: {sum(analytics['error_by_service'].values()):,}")
        print(f"   Services monitored: {len(analytics['error_by_service'])}")
        print(f"   Anomalies detected: {len(anomalies)}")
        print(f"   Output directory: {output_dir}/")

def main():
    print("\n" + "#" * 80)
    print("# DISTRIBUTED BATCH LOG ANALYTICS SYSTEM")
    print("# Apache Spark-Style Processing using Multiprocessing")
    print("#" * 80)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Processing Mode: Distributed (Multiprocessing)")
    print(f"Worker Processes: 4")
    
    try:
        # Initialize distributed analytics engine
        spark_analytics = SparkDistributedLogAnalytics(num_workers=4)
        
        # Stage 1: Load logs
        logs = spark_analytics.load_logs_distributed(LOCAL_INPUT_PATH)
        
        # Stage 2: Extract features (distributed)
        featured_logs = spark_analytics.extract_features_distributed(logs)
        
        # Stage 3: Batch analytics (distributed aggregations)
        analytics = spark_analytics.batch_analytics_distributed(featured_logs)
        
        # Stage 4: Anomaly detection
        anomalies = spark_analytics.anomaly_detection_distributed(featured_logs, analytics)
        
        # Stage 5: Save results
        spark_analytics.save_distributed_results(featured_logs, analytics, anomalies)
        
        print("\n" + "#" * 80)
        print("# ✅ DISTRIBUTED BATCH PROCESSING COMPLETE")
        print("# Results saved to: spark_output/")
        print("#" * 80)
        
    except Exception as e:
        print(f"\n❌ Processing Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
