"""
Distributed Log Generator
Simulates large-scale log generation from cloud infrastructure.
Generates realistic logs for batch processing and testing.
The final cloud demo uses large file-based batch processing.
"""

import json
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SERVICES = [
    'auth-service', 'api-gateway', 'payment-service', 
    'user-service', 'inventory-service', 'notification-service',
    'cache-service', 'database-service', 'analytics-engine'
]

LOG_LEVELS = {
    'DEBUG': 5,
    'INFO': 40,
    'WARNING': 30,
    'ERROR': 20,
    'CRITICAL': 5
}

NODES = [f'node-{i}' for i in range(1, 11)]

def generate_log():
    """Generate a realistic log entry."""
    
    level = random.choices(
        list(LOG_LEVELS.keys()),
        weights=list(LOG_LEVELS.values())
    )[0]
    
    service = random.choice(SERVICES)
    node = random.choice(NODES)
    
    # Generate realistic messages based on log level
    messages = {
        'DEBUG': [
            f'Cache hit for key {random.randint(1000, 9999)}',
            f'Query executed in {random.randint(1, 100)}ms',
            f'Connection pool size: {random.randint(5, 50)}',
        ],
        'INFO': [
            'User login successful',
            f'Transaction completed successfully',
            'Database replication healthy',
        ],
        'WARNING': [
            f'CPU usage at {random.randint(70, 99)}%',
            f'Memory consumption high: {random.randint(70, 95)}%',
            f'Response time elevated: {random.randint(500, 2000)}ms',
        ],
        'ERROR': [
            f'Failed to connect to database',
            f'Disk failure detected on {node}',
            f'Authentication failed for user request',
            f'OutOfMemory exception in {service}',
        ],
        'CRITICAL': [
            f'Cluster node {node} failed',
            f'Data corruption detected',
            f'Service {service} is down',
        ]
    }
    
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level,
        'service': service,
        'node': node,
        'message': random.choice(messages[level]),
        'request_id': f'req-{random.randint(100000, 999999)}',
        'duration_ms': random.randint(10, 5000),
        'status_code': random.choices([200, 201, 400, 401, 500], weights=[70, 10, 10, 5, 5])[0]
    }

def generate_logs_to_file(output_file, count=10000, rate=1000):
    """
    Generate logs and write to JSON file.
    rate: logs per second (for rate limiting)
    """
    print(f"Generating {count} logs to {output_file}...")
    
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        for i in range(count):
            log = generate_log()
            f.write(json.dumps(log) + '\n')
            
            if (i + 1) % rate == 0:
                elapsed = (i + 1) / rate
                print(f"  Generated {i + 1}/{count} logs ({elapsed:.1f} seconds)")
    
    print(f"✓ Completed: {count} logs saved to {output_file}")

def generate_large_scale_dataset(base_dir='data/', num_files=10, logs_per_file=100000):
    """
    Generate large-scale distributed log dataset.
    Simulates multiple log sources over time.
    """
    print("=" * 60)
    print("GENERATING LARGE-SCALE DISTRIBUTED LOG DATASET")
    print("=" * 60)
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    
    total_logs = 0
    
    for file_num in range(num_files):
        timestamp = datetime.utcnow() - timedelta(days=num_files-file_num)
        date_str = timestamp.strftime('%Y%m%d')
        
        output_file = Path(base_dir) / f"logs_{date_str}_batch{file_num:02d}.json"
        
        print(f"\nGenerating file {file_num+1}/{num_files}: {output_file.name}")
        generate_logs_to_file(str(output_file), count=logs_per_file)
        
        total_logs += logs_per_file
    
    print("\n" + "=" * 60)
    print(f"DATASET GENERATION COMPLETE")
    print(f"Total logs generated: {total_logs:,}")
    print(f"Location: {Path(base_dir).absolute()}")
    print("=" * 60)

if __name__ == '__main__':
    # Generate small dataset for quick testing
    generate_logs_to_file('data/sample_logs.json', count=10000, rate=1000)
    
    # Uncomment for large-scale dataset generation (warning: takes time)
    # generate_large_scale_dataset(base_dir='data/', num_files=10, logs_per_file=100000)
