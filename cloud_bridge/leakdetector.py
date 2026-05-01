import xgboost as xgb
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import db
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from .env

# Use variables instead of hardcoded paths
cred_path = os.getenv('FIREBASE_KEY_PATH')
db_url = os.getenv('DATABASE_URL')
model_path = os.getenv('MODEL_PATH')

# Initialize Firebase with the variable
cred = firebase_admin.credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {'databaseURL': db_url})

# Load model using the variable
model.load_model(model_path)
# --- CONFIGURATION ---
WINDOW_SIZE = 30
PREDICTION_HISTORY_SIZE = 5  # We look at the last 5 seconds of predictions
STABLE_THRESHOLD = 3         # Require at least 3 out of 5 to confirm a leak

def create_features(df):
    """Create rolling-normalized features using Title Case names"""
    df = df.copy()
    
    # 1. Normalize Flows
    f1_min = df['Flow_1_LPM'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    f1_max = df['Flow_1_LPM'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    f2_min = df['Flow_2_LPM'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    f2_max = df['Flow_2_LPM'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    
    df['Flow_1_LPM_Norm'] = (df['Flow_1_LPM'] - f1_min) / (f1_max - f1_min + 1e-6)
    df['Flow_2_LPM_Norm'] = (df['Flow_2_LPM'] - f2_min) / (f2_max - f2_min + 1e-6)
    
    # 2. Flow Divergence
    df['flow_div'] = df['Flow_1_LPM'] - df['Flow_2_LPM']
    flow_div_min = df['flow_div'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    flow_div_max = df['flow_div'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    df['Flow_Div_Norm'] = (df['flow_div'] - flow_div_min) / (flow_div_max - flow_div_min + 1e-6)
    df['Flow_Div_Trend'] = df['flow_div'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    
    # 3. Normalize Pressures
    p1_min = df['Pressure_1_SPU'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    p1_max = df['Pressure_1_SPU'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    p2_min = df['Pressure_2_SPU'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    p2_max = df['Pressure_2_SPU'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    
    df['Pres_1_SPU_Norm'] = (df['Pressure_1_SPU'] - p1_min) / (p1_max - p1_min + 1e-6)
    df['Pres_2_SPU_Norm'] = (df['Pressure_2_SPU'] - p2_min) / (p2_max - p2_min + 1e-6)
    
    # 4. Pressure Divergence
    df['pres_div'] = df['Pressure_2_SPU'] - df['Pressure_1_SPU']
    pres_div_min = df['pres_div'].rolling(window=WINDOW_SIZE, min_periods=1).min()
    pres_div_max = df['pres_div'].rolling(window=WINDOW_SIZE, min_periods=1).max()
    df['Pres_Div_Norm'] = (df['pres_div'] - pres_div_min) / (pres_div_max - pres_div_min + 1e-6)
    df['Pres_Div_Trend'] = df['pres_div'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    
    return df.fillna(0)

def is_reading_complete(reading):
    required_fields = ['timestamp', 'p1_spu', 'f1_lmin', 'f2_lmin', 'p2_spu']
    return all(field in reading for field in required_fields)

def get_readings_from_firebase():
    try:
        ref = db.reference('sensor_readings') 
        data_raw = ref.get()
        if not data_raw: return []
        readings = []
        if isinstance(data_raw, dict):
            for ts_key, val in data_raw.items():
                if isinstance(val, dict):
                    item = val.copy()
                    item['timestamp'] = int(ts_key)
                    if is_reading_complete(item): readings.append(item)
        elif isinstance(data_raw, list):
            for idx, val in enumerate(data_raw):
                if isinstance(val, dict):
                    item = val.copy()
                    item['timestamp'] = item.get('timestamp', idx) 
                    if is_reading_complete(item): readings.append(item)
        readings.sort(key=lambda x: x['timestamp'])
        return readings
    except Exception as e:
        print(f"❌ Error fetching from Firebase: {e}")
        return []

def update_firebase_label(timestamp, label):
    try:
        ref = db.reference(f'sensor_readings/{timestamp}/label')
        ref.set(label)
        return True
    except Exception as e:
        print(f"❌ Error updating Firebase: {e}")
        return False

def detect_leak():
    last_checked_timestamp = 0
    prediction_history = []  # Buffer for Majority Vote
    
    print("🚀 Stabilized Leak Detector Active")
    print(f"📊 Mode: Majority Vote ({STABLE_THRESHOLD}/{PREDICTION_HISTORY_SIZE})\n")
    
    while True:
        try:
            readings = get_readings_from_firebase()
            if len(readings) < WINDOW_SIZE:
                print(f"⏳ Buffering... {len(readings)}/{WINDOW_SIZE}", end='\r')
                time.sleep(1)
                continue
            
            new_readings = [r for r in readings if r['timestamp'] > last_checked_timestamp]
            if not new_readings:
                time.sleep(1)
                continue
            
            for reading in new_readings:
                idx = next((i for i, r in enumerate(readings) if r['timestamp'] == reading['timestamp']), None)
                if idx is None or idx < WINDOW_SIZE - 1:
                    last_checked_timestamp = reading['timestamp']
                    continue
                
                window = readings[idx - WINDOW_SIZE + 1:idx + 1]
                df = pd.DataFrame([{
                    'Flow_1_LPM': r['f1_lmin'],
                    'Flow_2_LPM': r['f2_lmin'],
                    'Pressure_1_SPU': r['p1_spu'],
                    'Pressure_2_SPU': r['p2_spu'],
                } for r in window])
                
                # 1. Prediction
                df_feat = create_features(df)
                latest_features = df_feat.iloc[-1]
                features = np.array([[
                    latest_features['Flow_1_LPM_Norm'], latest_features['Flow_2_LPM_Norm'],
                    latest_features['Flow_Div_Norm'], latest_features['Flow_Div_Trend'],
                    latest_features['Pres_1_SPU_Norm'], latest_features['Pres_2_SPU_Norm'],
                    latest_features['Pres_Div_Norm'], latest_features['Pres_Div_Trend'],
                ]])
                
                raw_pred = int(model.predict(features)[0])
                confidence = float(model.predict_proba(features)[0][1])

                # NEW: Only count it as a "Raw Leak" if confidence is high
                if raw_pred == 1 and confidence < 0.80:
                    raw_pred = 0  # Treat low-confidence detections as Normal noise

                # 2. Majority Vote (Temporal Filtering)
                prediction_history.append(raw_pred)
                if len(prediction_history) > PREDICTION_HISTORY_SIZE:
                    prediction_history.pop(0)
                
                # A "Stable" leak requires at least 3/5 raw detections
                stable_pred = 1 if sum(prediction_history) >= STABLE_THRESHOLD else 0
                
                # 3. Logging & Firebase Update
                status = "🚨 LEAK" if stable_pred == 1 else "✅ NORMAL"
                print(f"[{reading['timestamp']}] {status} (Raw: {raw_pred}, Conf: {confidence:.2f}, History: {sum(prediction_history)}/5)")
                
                update_firebase_label(reading['timestamp'], stable_pred)
                last_checked_timestamp = reading['timestamp']
            
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    detect_leak()
