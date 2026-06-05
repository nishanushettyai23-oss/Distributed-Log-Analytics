"""
Machine Learning Training Module for Anomaly Detection
Trains models using HDFS dataset files for log anomaly detection.
Supports Isolation Forest and Local Outlier Factor algorithms.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.model_selection import train_test_split
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

class LogAnomalyDetectionMLModel:
    """Machine Learning Model for HDFS Log Anomaly Detection"""
    
    def __init__(self, model_type='isolation_forest', random_state=42):
        """Initialize the ML model"""
        self.model_type = model_type
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.training_stats = {}
    
    def load_dataset(self, dataset_name):
        """Load a specific HDFS dataset"""
        if dataset_name not in HDFS_DATASETS:
            raise ValueError(f"Dataset {dataset_name} not found. Available: {list(HDFS_DATASETS.keys())}")
        
        csv_path = DATASET_PATH / HDFS_DATASETS[dataset_name]
        
        print(f"\n{'='*70}")
        print(f"Loading Dataset: {dataset_name}")
        print(f"{'='*70}")
        print(f"Path: {csv_path}")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        print(f"✓ Loaded {len(df)} rows")
        print(f"✓ Columns: {list(df.columns)}")
        print(f"\nFirst 5 rows:")
        print(df.head())
        
        return df
    
    def preprocess_data(self, df):
        """
        Preprocess log data for ML training.
        Handles categorical variables and feature engineering.
        """
        print(f"\n{'='*70}")
        print("DATA PREPROCESSING")
        print(f"{'='*70}")
        
        df_processed = df.copy()
        
        # Handle missing values
        print(f"Missing values:\n{df_processed.isnull().sum()}")
        df_processed = df_processed.fillna(0)
        
        # Select numeric features for anomaly detection
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclude label columns if present
        if 'Label' in numeric_cols:
            numeric_cols.remove('Label')
        if 'EventId' in numeric_cols:
            numeric_cols.remove('EventId')
        
        print(f"\n✓ Using {len(numeric_cols)} numeric features for training")
        print(f"  Features: {numeric_cols}")
        
        self.feature_names = numeric_cols
        X = df_processed[numeric_cols].values
        
        # Get labels if available
        y = None
        if 'Label' in df_processed.columns:
            y = df_processed['Label'].values
            print(f"\n✓ Found labels: {np.unique(y)}")
        
        return X, y, df_processed
    
    def train_model(self, X, y=None, contamination=0.1, test_size=0.2):
        """
        Train anomaly detection model using the provided dataset.
        
        Args:
            X: Feature matrix
            y: Labels (optional, for evaluation)
            contamination: Expected fraction of anomalies
            test_size: Fraction for test set
        """
        print(f"\n{'='*70}")
        print("MODEL TRAINING")
        print(f"{'='*70}")
        
        # Split data
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state, stratify=y
            )
        else:
            X_train, X_test = train_test_split(
                X, test_size=test_size, random_state=self.random_state
            )
            y_train, y_test = None, None
        
        print(f"Training set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        # Scale features
        print(f"\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print(f"\nTraining {self.model_type} model...")
        
        if self.model_type == 'isolation_forest':
            self.model = IsolationForest(
                contamination=contamination,
                random_state=self.random_state,
                n_jobs=-1
            )
        elif self.model_type == 'local_outlier_factor':
            self.model = LocalOutlierFactor(
                n_neighbors=20,
                contamination=contamination,
                novelty=True,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X_train_scaled)
        
        # Predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # Calculate statistics
        train_anomalies = np.sum(y_train_pred == -1)
        test_anomalies = np.sum(y_test_pred == -1)
        
        print(f"\n✓ Model trained successfully!")
        print(f"\nTraining Results:")
        print(f"  Anomalies detected in training set: {train_anomalies} ({100*train_anomalies/len(y_train_pred):.1f}%)")
        print(f"  Anomalies detected in test set: {test_anomalies} ({100*test_anomalies/len(y_test_pred):.1f}%)")
        
        # Evaluation with labels if available
        if y_test is not None:
            from sklearn.metrics import classification_report, confusion_matrix
            print(f"\nEvaluation Metrics (Test Set):")
            print(f"\nConfusion Matrix:")
            print(confusion_matrix(y_test, y_test_pred))
            print(f"\nClassification Report:")
            print(classification_report(y_test, y_test_pred, target_names=['Normal', 'Anomaly']))
        
        self.training_stats = {
            'model_type': self.model_type,
            'training_samples': X_train.shape[0],
            'test_samples': X_test.shape[0],
            'features': self.feature_names,
            'train_anomalies': int(train_anomalies),
            'test_anomalies': int(test_anomalies),
            'contamination': contamination,
            'trained_at': datetime.now().isoformat()
        }
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train_pred,
            'y_test': y_test_pred
        }
    
    def save_model(self, model_name):
        """Save trained model and scaler"""
        MODEL_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        
        model_path = MODEL_OUTPUT_PATH / f"{model_name}_model.pkl"
        scaler_path = MODEL_OUTPUT_PATH / f"{model_name}_scaler.pkl"
        stats_path = MODEL_OUTPUT_PATH / f"{model_name}_stats.json"
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        with open(stats_path, 'w') as f:
            json.dump(self.training_stats, f, indent=2)
        
        print(f"\n{'='*70}")
        print("MODEL SAVED")
        print(f"{'='*70}")
        print(f"✓ Model: {model_path}")
        print(f"✓ Scaler: {scaler_path}")
        print(f"✓ Stats: {stats_path}")
        
        return {
            'model_path': str(model_path),
            'scaler_path': str(scaler_path),
            'stats_path': str(stats_path)
        }
    
    def load_model(self, model_name):
        """Load a trained model"""
        model_path = MODEL_OUTPUT_PATH / f"{model_name}_model.pkl"
        scaler_path = MODEL_OUTPUT_PATH / f"{model_name}_scaler.pkl"
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        print(f"✓ Loaded model: {model_path}")
        print(f"✓ Loaded scaler: {scaler_path}")
    
    def predict_anomalies(self, X):
        """Predict anomalies on new data"""
        if self.model is None:
            raise ValueError("Model not trained. Train or load a model first.")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Get anomaly scores
        if hasattr(self.model, 'score_samples'):
            scores = self.model.score_samples(X_scaled)
        else:
            scores = np.zeros(len(predictions))
        
        return predictions, scores

def train_all_datasets():
    """Train models on all available HDFS datasets"""
    results = {}
    
    for dataset_name in HDFS_DATASETS.keys():
        print(f"\n\n{'#'*70}")
        print(f"# Training on {dataset_name}")
        print(f"{'#'*70}")
        
        try:
            # Initialize model
            model = LogAnomalyDetectionMLModel(model_type='isolation_forest')
            
            # Load and preprocess data
            df = model.load_dataset(dataset_name)
            X, y, df_processed = model.preprocess_data(df)
            
            # Train model
            model.train_model(X, y, contamination=0.1)
            
            # Save model
            saved_paths = model.save_model(f"hdfs_{dataset_name}")
            
            results[dataset_name] = {
                'status': 'success',
                'paths': saved_paths,
                'stats': model.training_stats
            }
            
        except Exception as e:
            print(f"✗ Error training on {dataset_name}: {e}")
            results[dataset_name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    return results

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  HDFS LOG ANOMALY DETECTION - ML TRAINING")
    print("="*70)
    
    # Train on all datasets
    results = train_all_datasets()
    
    # Summary
    print(f"\n\n{'='*70}")
    print("TRAINING SUMMARY")
    print(f"{'='*70}")
    
    for dataset_name, result in results.items():
        if result['status'] == 'success':
            print(f"\n✓ {dataset_name}: SUCCESS")
            print(f"  Model: {result['paths']['model_path']}")
        else:
            print(f"\n✗ {dataset_name}: FAILED - {result['error']}")
    
    print(f"\n{'='*70}\n")
