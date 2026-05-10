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

FEATURE_COLS = [
    'F1_Lmin_Norm',
    'F2_Lmin_Norm',
    'Flow_Div_Norm',
    'Flow_Div_Trend',
    'P1_SPU_Norm',
    'P2_SPU_Norm',
    'Pres_Div_Norm',
    'Pres_Div_Trend'
]

# Load model using the variable
model = xgb.XGBClassifier()
model.load_model(model_path)
# --- CONFIGURATION ---
WINDOW_SIZE = 30
PREDICTION_HISTORY_SIZE = 5  # We look at the last 5 seconds of predictions
STABLE_THRESHOLD = 3         # Require at least 3 out of 5 to confirm a leak

MAX_FLOW = 30.0  # Max LPM for YF-S201
MAX_PRES = 1200.0 # Max SPU for your pressure sensors

# --- CONFIGURATION CONSTANTS ---
# Based on your hardware analysis
MAX_FLOW_LEAK = 2.5   # The max LPM divergence you expect (observed 2.14)
MAX_PRES_DIV = 10.0   # Scale for pressure divergence
FLOW_DEADBAND = 0.3   # Ignore anything below 0.3 LPM (clears your 0.27 noise)

def create_features(df):
    df = df.copy()
    
    # 1. Flow Divergence with Deadband
    df['flow_div_raw'] = df['Flow_1_LPM'] - df['Flow_2_LPM']
    # If noise is within deadband, force to 0
    df.loc[df['flow_div_raw'].abs() < FLOW_DEADBAND, 'flow_div_raw'] = 0
    
    # 2. Fixed Normalization (No more rolling min-max!)
    # Map 0 -> 0.0 and MAX_FLOW_LEAK -> 1.0
    df['Flow_Div_Norm'] = (df['flow_div_raw'] / MAX_FLOW_LEAK).clip(0, 1)
    df['Flow_Div_Trend'] = df['flow_div_raw'].rolling(window=30, min_periods=1).mean()
    
    # 3. Individual Flow Scaling (YF-S201 Max is ~30 LPM)
    df['F1_Lmin_Norm'] = (df['Flow_1_LPM'] / 30.0).clip(0, 1)
    df['F2_Lmin_Norm'] = (df['Flow_2_LPM'] / 30.0).clip(0, 1)
    
    # 4. Pressure Divergence Scaling
    df['pres_div_raw'] = df['Pressure_2_SPU'] - df['Pressure_1_SPU']
    df['Pres_Div_Norm'] = (df['pres_div_raw'] / MAX_PRES_DIV).clip(-1, 1)
    df['Pres_Div_Trend'] = df['pres_div_raw'].rolling(window=30, min_periods=1).mean()
    
    # 5. Individual Pressure Scaling (HK1100C Max is 1200 kPa)
    df['P1_SPU_Norm'] = (df['Pressure_1_SPU'] / 1200.0).clip(0, 1)
    df['P2_SPU_Norm'] = (df['Pressure_2_SPU'] / 1200.0).clip(0, 1)
    
    return df[FEATURE_COLS].fillna(0)
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
                    item['timestamp'] = ts_key
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
    last_checked_timestamp = ""
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
                features = df_feat.tail(1)
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
