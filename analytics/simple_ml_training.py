"""
Simple ML Training Module - Uses CSV parsing without pandas
Trains anomaly detection model on HDFS dataset CSV files.
"""

import csv
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
import json
from datetime import datetime

# Configuration
DATASET_PATH = Path("dataset/")
MODEL_OUTPUT_PATH = Path("models/")

HDFS_DATASETS = {
    "HDFS_2k": "HDFS_2k/HDFS_2k.log_structured.csv",
    "HDFS_v1": "HDFS_v1/HDFS_v1.log_structured.csv",
    "HDFS_v2": "HDFS_v2/HDFS_v2.log_structured.csv",
    "HDFS_v3": "HDFS_v3_TraceBench/HDFS_v3_TraceBench.log_structured.csv"
}

def load_csv_data(csv_path):
    """Load CSV file and extract numeric features"""
    print(f"Loading: {csv_path}")
    
    data = []
    headers = []
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Get headers
        
        for i, row in enumerate(reader):
            if i < 5:
                print(f"  Sample row {i}: {row[:5]}...")
            data.append(row)
    
    print(f"✓ Loaded {len(data)} rows with {len(headers)} columns")
    print(f"  Columns: {headers}")
    
    # Extract numeric features
    numeric_data = []
    for row in data:
        numeric_row = []
        for val in row:
            try:
                numeric_row.append(float(val))
            except ValueError:
                numeric_row.append(0)
        numeric_data.append(numeric_row)
    
    return np.array(numeric_data, dtype=np.float32), headers

def train_model(X, model_name, contamination=0.1):
    """Train Isolation Forest model"""
    print(f"\n{'='*70}")
    print(f"Training Model: {model_name}")
    print(f"{'='*70}")
    
    print(f"Data shape: {X.shape}")
    print(f"Features: {X.shape[1]}")
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    print(f"Training Isolation Forest (contamination={contamination})...")
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )
    
    predictions = model.fit_predict(X_scaled)
    
    # Calculate statistics
    n_anomalies = np.sum(predictions == -1)
    anomaly_pct = 100 * n_anomalies / len(predictions)
    
    print(f"\n✓ Model trained!")
    print(f"  Anomalies detected: {n_anomalies} ({anomaly_pct:.1f}%)")
    print(f"  Normal samples: {np.sum(predictions == 1)} ({100-anomaly_pct:.1f}%)")
    
    return model, scaler, predictions

def save_model(model, scaler, model_name, dataset_name):
    """Save trained model and scaler"""
    MODEL_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    model_path = MODEL_OUTPUT_PATH / f"{model_name}_model.pkl"
    scaler_path = MODEL_OUTPUT_PATH / f"{model_name}_scaler.pkl"
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"\n✓ Model saved:")
    print(f"  {model_path}")
    print(f"  {scaler_path}")
    
    return str(model_path), str(scaler_path)

def main():
    print("\n" + "="*70)
    print("  HDFS LOG ANOMALY DETECTION - ML TRAINING")
    print("="*70)
    
    results = {}
    
    for dataset_name, csv_file in HDFS_DATASETS.items():
        csv_path = DATASET_PATH / csv_file
        
        if not csv_path.exists():
            print(f"\n⚠ Dataset not found: {csv_path}")
            results[dataset_name] = {'status': 'not_found'}
            continue
        
        print(f"\n\n{'#'*70}")
        print(f"# {dataset_name}")
        print(f"{'#'*70}")
        
        try:
            # Load data
            X, headers = load_csv_data(csv_path)
            
            # Train model
            model, scaler, predictions = train_model(
                X, 
                dataset_name,
                contamination=0.1
            )
            
            # Save model
            model_path, scaler_path = save_model(
                model,
                scaler,
                f"hdfs_{dataset_name}",
                dataset_name
            )
            
            results[dataset_name] = {
                'status': 'success',
                'model_path': model_path,
                'scaler_path': scaler_path,
                'samples': X.shape[0],
                'features': X.shape[1],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            results[dataset_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    # Print summary
    print(f"\n\n{'='*70}")
    print("TRAINING SUMMARY")
    print(f"{'='*70}")
    
    for dataset_name, result in results.items():
        if result['status'] == 'success':
            print(f"\n✓ {dataset_name}")
            print(f"  Samples: {result['samples']}")
            print(f"  Features: {result['features']}")
            print(f"  Model: {Path(result['model_path']).name}")
        elif result['status'] == 'not_found':
            print(f"\n⚠ {dataset_name}: Dataset file not found")
        else:
            print(f"\n✗ {dataset_name}: {result.get('error', 'Unknown error')}")
    
    # Save results
    results_path = MODEL_OUTPUT_PATH / "training_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved: {results_path}\n")

if __name__ == "__main__":
    main()
