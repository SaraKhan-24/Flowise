import xgboost as xgb
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import db, credentials
import time
import os
import streamlit as st
import json
from datetime import datetime, timedelta

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Flowise 24/7 Monitor", page_icon="🌊", layout="wide")
st.title("🌊 Flowise Real-Time Leak Detection")

# Sidebar for connection info
with st.sidebar:
    st.header("Hardware Status")
    conn_status = st.empty()
    last_sync_time = st.empty()
    st.divider()
    st.info("This system runs 24/7. It will automatically pause if the ESP32 goes offline.")

# Main Dashboard UI
status_col, metric_col = st.columns([1, 1])
with status_col:
    st.subheader("System Status")
    status_placeholder = st.empty()
with metric_col:
    st.subheader("Live Flow Rates")
    m_col1, m_col2 = st.columns(2)
    f1_metric = m_col1.empty()
    f2_metric = m_col2.empty()

st.divider()
log_placeholder = st.expander("Detection History", expanded=True)

# --- CONFIGURATION ---
WINDOW_SIZE = 30
OFFLINE_TIMEOUT = 20 # Mark as offline if no update in 20 seconds

# --- INITIALIZATION ---
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            if "FIREBASE_SERVICE_ACCOUNT" in st.secrets:
                cred_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
                db_url = st.secrets.get("DATABASE_URL")
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred, {'databaseURL': db_url})
                return True
            return False
        except Exception: return False
    return True

@st.cache_resource
def load_model():
    try:
        model = xgb.XGBClassifier()
        model.load_model("xgb_leak_detector_hardware_finetuned.json")
        return model
    except: return None

def create_features(df):
    df = df.copy()
    # Logic same as leakdetector.py
    df['flow_div_raw'] = df['Flow_1_LPM'] - df['Flow_2_LPM']
    df.loc[df['flow_div_raw'].abs() < 0.3, 'flow_div_raw'] = 0
    df['Flow_Div_Norm'] = (df['flow_div_raw'] / 2.5).clip(0, 1)
    df['Flow_Div_Trend'] = df['flow_div_raw'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    df['F1_Lmin_Norm'] = (df['Flow_1_LPM'] / 30.0).clip(0, 1)
    df['F2_Lmin_Norm'] = (df['Flow_2_LPM'] / 30.0).clip(0, 1)
    df['pres_div_raw'] = df['Pressure_2_SPU'] - df['Pressure_1_SPU']
    df['Pres_Div_Norm'] = (df['pres_div_raw'] / 10.0).clip(-1, 1)
    df['Pres_Div_Trend'] = df['pres_div_raw'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    df['P1_SPU_Norm'] = (df['Pressure_1_SPU'] / 1200.0).clip(0, 1)
    df['P2_SPU_Norm'] = (df['Pressure_2_SPU'] / 1200.0).clip(0, 1)
    
    cols = ['F1_Lmin_Norm', 'F2_Lmin_Norm', 'Flow_Div_Norm', 'Flow_Div_Trend',
            'P1_SPU_Norm', 'P2_SPU_Norm', 'Pres_Div_Norm', 'Pres_Div_Trend']
    return df[cols].fillna(0)

# --- THE 24/7 AUTO-LOOP ---
if initialize_firebase():
    conn_status.success("Connected to Firebase")
    model = load_model()
    
    if model:
        last_processed_key = None
        last_update_wall_time = time.time() # To track inactivity
        prediction_history = []
        logs = []

        while True:
            try:
                ref = db.reference('sensor_readings')
                data_raw = ref.order_by_key().limit_to_last(1).get()
                
                if data_raw:
                    latest_key = list(data_raw.keys())[0]
                    latest_val = data_raw[latest_key]
                    
                    # 1. CHECK IF SYSTEM IS FRESH
                    if latest_key != last_processed_key:
                        # Reset the inactivity timer because we got a new value!
                        last_update_wall_time = time.time()
                        
                        # Process the new data...
                        data_batch = ref.order_by_key().limit_to_last(WINDOW_SIZE).get()
                        sorted_keys = sorted(data_batch.keys())
                        rows = [{'Flow_1_LPM': data_batch[k].get('f1_lmin', 0),
                                 'Flow_2_LPM': data_batch[k].get('f2_lmin', 0),
                                 'Pressure_1_SPU': data_batch[k].get('p1_spu', 0),
                                 'Pressure_2_SPU': data_batch[k].get('p2_spu', 0)} for k in sorted_keys]
                        
                        df = pd.DataFrame(rows)
                        features = create_features(df).tail(1)
                        raw_pred = int(model.predict(features)[0])
                        confidence = float(model.predict_proba(features)[0][1])

                        if raw_pred == 1 and confidence < 0.80: raw_pred = 0
                        prediction_history.append(raw_pred)
                        if len(prediction_history) > 5: prediction_history.pop(0)
                        stable_pred = 1 if sum(prediction_history) >= 3 else 0

                        # Update Firebase historical log
                        db.reference(f'sensor_readings/{latest_key}/label').set(stable_pred)
                        
                        # Sync live snapshot to 'sensors' node matching Flutter mobile app schema
                        db.reference('sensors').set({
                            'F1': latest_val.get('f1_lmin', 0),
                            'F2': latest_val.get('f2_lmin', 0),
                            'P1': latest_val.get('p1_spu', 0),
                            'P2': latest_val.get('p2_spu', 0),
                            'Leak': stable_pred
                        })
                        
                        # Update UI with Active state
                        f1_metric.metric("Flow 1", f"{latest_val.get('f1_lmin',0):.2f} L/min")
                        f2_metric.metric("Flow 2", f"{latest_val.get('f2_lmin',0):.2f} L/min")
                        
                        if stable_pred == 1:
                            status_placeholder.error("🚨 LEAK DETECTED!")
                        else:
                            status_placeholder.success("✅ System Normal")

                        logs.insert(0, f"[{latest_key}] Status: {'LEAK' if stable_pred else 'Normal'}")
                        with log_placeholder: st.code("\n".join(logs[:5]))
                        
                        last_processed_key = latest_key
                        last_sync_time.info(f"Last Sync: {latest_key}")

                # 2. OFFLINE DETECTION
                # If no NEW data has arrived in the last 20 seconds
                if time.time() - last_update_wall_time > OFFLINE_TIMEOUT:
                    status_placeholder.warning("📡 ESP32 Offline - Monitoring Paused")
                    f1_metric.metric("Flow 1", "0.00 L/min (Off)")
                    f2_metric.metric("Flow 2", "0.00 L/min (Off)")
                
                time.sleep(2)
            except Exception as e:
                time.sleep(5)
