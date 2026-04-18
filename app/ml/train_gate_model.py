#!/usr/bin/env python3
"""
Smart Stadium ML - Phase ML-2: Gate Load Predictor

Trains an XGBoost model to predict queue depth at each gate 10 and 30 minutes ahead.
This replaces the hard-coded 80% threshold rerouting with proactive ML-driven predictions.

Usage: python app/ml/train_gate_model.py
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

print("\n" + "="*70)
print("  PHASE ML-2: GATE LOAD PREDICTOR - XGBOOST")
print("="*70)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n[1/5] Loading gate load data...")

gate_loads_file = Path("data/generated/gate_loads.csv")
df = pd.read_csv(gate_loads_file)

print(f"✓ Loaded {len(df):,} records")
print(f"  Features: {list(df.columns)}")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n[2/5] Engineering features...")

# Create prediction targets: queue depth at T+10 and T+30
df = df.sort_values(['event_id', 'gate_id', 'timestamp_minute']).reset_index(drop=True)

# For each record, look ahead to T+10 and T+30
df['target_t10'] = 0
df['target_t30'] = 0

for gate in df['gate_id'].unique():
    for event in df['event_id'].unique():
        gate_event_data = df[(df['gate_id'] == gate) & (df['event_id'] == event)]
        
        for idx, row in gate_event_data.iterrows():
            current_minute = row['timestamp_minute']
            
            # Find records at T+10 and T+30
            t10_data = df[(df['gate_id'] == gate) & (df['event_id'] == event) & 
                         (df['timestamp_minute'] == current_minute + 10)]
            t30_data = df[(df['gate_id'] == gate) & (df['event_id'] == event) & 
                         (df['timestamp_minute'] == current_minute + 30)]
            
            if not t10_data.empty:
                df.loc[idx, 'target_t10'] = t10_data['queue_depth'].values[0]
            if not t30_data.empty:
                df.loc[idx, 'target_t30'] = t30_data['queue_depth'].values[0]

# Feature engineering
df['is_peak_time'] = ((df['timestamp_minute'] >= 10) & (df['timestamp_minute'] <= 30)).astype(int)
df['pre_match'] = (df['timestamp_minute'] < -10).astype(int)
df['rainy'] = (df['weather'] == 'rain').astype(int)
df['extreme_weather'] = (df['weather'] == 'extreme').astype(int)
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

# Encode categorical variables
le_weather = LabelEncoder()
le_event = LabelEncoder()
le_gate = LabelEncoder()

df['weather_encoded'] = le_weather.fit_transform(df['weather'])
df['event_type_encoded'] = le_event.fit_transform(df['event_type'])
df['gate_encoded'] = le_gate.fit_transform(df['gate_id'])

print("✓ Feature engineering complete")
print(f"  Created synthetic features: is_peak_time, pre_match, rainy, extreme_weather, is_weekend")
print(f"  Targets: target_t10, target_t30")

# ============================================================================
# STEP 3: PREPARE TRAINING DATA
# ============================================================================
print("\n[3/5] Preparing training data...")

# Feature set
feature_cols = [
    'timestamp_minute',
    'attendees_passed',
    'is_peak_time',
    'pre_match',
    'rainy',
    'extreme_weather',
    'is_weekend',
    'day_of_week',
    'gate_encoded',
    'event_type_encoded'
]

X = df[feature_cols].copy()
y_t10 = df['target_t10'].copy()
y_t30 = df['target_t30'].copy()

# Filter out rows without valid targets (edge cases)
valid_idx = (y_t10 > 0) | (y_t30 > 0)
X = X[valid_idx]
y_t10 = y_t10[valid_idx]
y_t30 = y_t30[valid_idx]

print(f"✓ Training set size: {len(X):,} records")
print(f"  Features: {len(feature_cols)}")

# Split data
X_train, X_test, y_t10_train, y_t10_test, y_t30_train, y_t30_test = train_test_split(
    X, y_t10, y_t30, test_size=0.2, random_state=42
)

print(f"  Train: {len(X_train):,}, Test: {len(X_test):,}")

# ============================================================================
# STEP 4: TRAIN MODELS
# ============================================================================
print("\n[4/5] Training XGBoost models...")

# Model for T+10 prediction
print("  Training T+10 predictor...")
model_t10 = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0
)
model_t10.fit(X_train, y_t10_train)

# Model for T+30 prediction
print("  Training T+30 predictor...")
model_t30 = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0
)
model_t30.fit(X_train, y_t30_train)

print("✓ Training complete")

# ============================================================================
# STEP 5: EVALUATE & SAVE
# ============================================================================
print("\n[5/5] Evaluating and saving models...")

from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Evaluate T+10
y_pred_t10 = model_t10.predict(X_test)
r2_t10 = r2_score(y_t10_test, y_pred_t10)
mae_t10 = mean_absolute_error(y_t10_test, y_pred_t10)
rmse_t10 = np.sqrt(mean_squared_error(y_t10_test, y_pred_t10))

print(f"\n📊 T+10 Model Metrics:")
print(f"  R² Score:  {r2_t10:.4f}")
print(f"  MAE:       {mae_t10:.2f} people")
print(f"  RMSE:      {rmse_t10:.2f} people")

# Evaluate T+30
y_pred_t30 = model_t30.predict(X_test)
r2_t30 = r2_score(y_t30_test, y_pred_t30)
mae_t30 = mean_absolute_error(y_t30_test, y_pred_t30)
rmse_t30 = np.sqrt(mean_squared_error(y_t30_test, y_pred_t30))

print(f"\n📊 T+30 Model Metrics:")
print(f"  R² Score:  {r2_t30:.4f}")
print(f"  MAE:       {mae_t30:.2f} people")
print(f"  RMSE:      {rmse_t30:.2f} people")

# Save models
model_dir = Path("app/ml/models")
model_dir.mkdir(parents=True, exist_ok=True)

with open(model_dir / "gate_load_t10.pkl", 'wb') as f:
    pickle.dump(model_t10, f)

with open(model_dir / "gate_load_t30.pkl", 'wb') as f:
    pickle.dump(model_t30, f)

# Save encoders
with open(model_dir / "gate_encoders.pkl", 'wb') as f:
    pickle.dump({
        'weather': le_weather,
        'event_type': le_event,
        'gate': le_gate
    }, f)

# Save feature names
with open(model_dir / "gate_features.pkl", 'wb') as f:
    pickle.dump(feature_cols, f)

print(f"\n✅ Models saved to {model_dir}")
print(f"  ✓ gate_load_t10.pkl")
print(f"  ✓ gate_load_t30.pkl")
print(f"  ✓ gate_encoders.pkl")
print(f"  ✓ gate_features.pkl")

# Feature importance
print(f"\n🔍 Top 5 Important Features (T+10):")
importances = model_t10.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': feature_cols,
    'importance': importances
}).sort_values('importance', ascending=False)

for idx, row in feature_importance_df.head(5).iterrows():
    print(f"  {row['feature']:25s} {row['importance']:7.4f}")

print("\n" + "="*70)
print("  ✅ PHASE ML-2 COMPLETE")
print("="*70)
print("\nNext: Use these models in inference_server.py to make real-time predictions")
