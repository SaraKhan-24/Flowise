import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import firebase_admin
from firebase_admin import db, credentials, messaging
import time
import os
import streamlit as st
import json
from datetime import datetime, timedelta

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Flowise 24/7 Monitor", page_icon="🌊", layout="wide")
st.title("🌊 Flowise Real-Time Leak Detection (Deep Learning Engine)")

with st.sidebar:
    st.header("Hardware Status")
    conn_status = st.empty()
    last_sync_time = st.empty()
    st.divider()
    st.info("This system runs a 1D-CNN + GRU sequence network 24/7. It automatically holds inference if the ESP32 goes offline.")

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
SEQ_LEN = 15          # Sliding sequence matrix size required by PyTorch
FETCH_LEN = 30        # Fetch 30 rows to provide warm-up history for rolling trends
OFFLINE_TIMEOUT = 20  # Mark system offline if telemetry halts for 20 seconds
FEATURE_COLS = ['Flow_Div_Ratio', 'Flow_Div_Trend', 'Pres_Drop_Ratio', 'Pres_Drop_Trend']

if 'priming_start_time' not in st.session_state:
    st.session_state['priming_start_time'] = None

# --- PyTorch MODEL DEFINITION ---
class FlowWiseHybridNet(nn.Module):
    def __init__(self, input_dim=4, conv_filters=32, gru_hidden=64, num_gru_layers=2):
        super(FlowWiseHybridNet, self).__init__()
        self.conv1d = nn.Conv1d(in_channels=input_dim, out_channels=conv_filters, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.gru = nn.GRU(input_size=conv_filters, hidden_size=gru_hidden, 
                          num_layers=num_gru_layers, batch_first=True)
        self.fc = nn.Linear(gru_hidden, 1)
        
    def forward(self, x):
        x = x.transpose(1, 2)
        x = self.relu(self.conv1d(x))
        x = x.transpose(1, 2)
        gru_out, _ = self.gru(x)
        last_timestep_features = gru_out[:, -1, :]
        return self.fc(last_timestep_features)

# --- INITIALIZATION ROUTINES ---
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
def load_pytorch_model():
    try:
        model = FlowWiseHybridNet(input_dim=len(FEATURE_COLS))
        model.load_state_dict(torch.load("flowwise_inverted_sequence_net.pth", map_location=torch.device('cpu')))
        model.eval() 
        return model
    except Exception as e:
        st.error(f"Failed to load PyTorch model: {e}")
        return None

# --- MATCHED SCALE-INVARIANT FEATURE ENGINE ---
def create_scale_invariant_features(df):
    df = df.copy()
    epsilon = 1e-6
    
    # Cast variables securely to numeric values
    f_up   = pd.to_numeric(df['Flow_1_LPM'], errors='coerce').fillna(0)
    f_down = pd.to_numeric(df['Flow_2_LPM'], errors='coerce').fillna(0)
    p_up   = pd.to_numeric(df['Pressure_1_SPU'], errors='coerce').fillna(0)
    p_down = pd.to_numeric(df['Pressure_2_SPU'], errors='coerce').fillna(0)
    
    # 1. Dimensionless Flow Divergence Fraction
    flow_div = (f_up - f_down) / (f_up + epsilon)
    flow_div[f_up < 0.1] = 0.0  
    
    # 2. Dimensionless Head Pressure Loss Fraction
    pres_drop = (p_up - p_down) / (p_up + epsilon)
    pres_drop[p_up < 1.0] = 0.0  

    df_out = pd.DataFrame()
    df_out['Flow_Div_Ratio']  = flow_div
    df_out['Flow_Div_Trend']  = flow_div.rolling(window=SEQ_LEN, min_periods=1).mean()
    df_out['Pres_Drop_Ratio'] = pres_drop
    df_out['Pres_Drop_Trend'] = pres_drop.rolling(window=SEQ_LEN, min_periods=1).mean()
    
    # Retain the 15-row slice populated with complete historical trends
    return df_out[FEATURE_COLS].tail(SEQ_LEN).fillna(0)

# --- NOTIFICATION TRIGGERS ---
def send_leak_notification():
    try:
        token_ref = db.reference("user_tokens/admin_token")
        registration_token = token_ref.get()
        if not registration_token: return
        message = messaging.Message(
            notification=messaging.Notification(
                title='🚨 Leak Detected!',
                body='FlowWise has detected an active water leak. Urgent action required!',
            ),
            android=messaging.AndroidConfig(
                ttl=timedelta(seconds=3600), priority='high',
                notification=messaging.AndroidNotification(icon='default', color='#F44336', sound='default'),
            ),
            token=registration_token,
        )
        messaging.send(message)
    except Exception: pass

def send_clear_notification():
    try:
        token_ref = db.reference("user_tokens/admin_token")
        registration_token = token_ref.get()
        if not registration_token: return
        message = messaging.Message(
            notification=messaging.Notification(
                title='✅ System Secure',
                body='The leak alert has cleared. The system is back to normal.',
            ),
            android=messaging.AndroidConfig(
                ttl=timedelta(seconds=3600), priority='high',
                notification=messaging.AndroidNotification(icon='default', color='#4CAF50', sound='default'),
            ),
            token=registration_token,
        )
        messaging.send(message)
    except Exception: pass

# --- THE 24/7 MONITORING LOOP ---
if initialize_firebase():
    conn_status.success("Connected to Firebase")
    model = load_pytorch_model()
    
    if model:
        last_processed_key = None
        last_update_wall_time = time.time() 
        prediction_history = []
        logs = []
        last_notified_state = 0 

        while True:
            try:
                ref = db.reference('sensor_readings')
                data_raw = ref.order_by_key().limit_to_last(1).get()
                
                if data_raw:
                    latest_key = list(data_raw.keys())[0]
                    latest_val = data_raw[latest_key]
                    
                    if latest_key != last_processed_key:
                        last_update_wall_time = time.time() 
                        
                        # Pull lookback frame sizes to ensure trends stay populated
                        data_batch = ref.order_by_key().limit_to_last(FETCH_LEN).get()
                        sorted_keys = sorted(data_batch.keys())
                        
                        rows = [{
                            'Flow_1_LPM': data_batch[k].get('f1_lmin', 0),
                            'Flow_2_LPM': data_batch[k].get('f2_lmin', 0),
                            'Pressure_1_SPU': data_batch[k].get('p1_spu', 0),
                            'Pressure_2_SPU': data_batch[k].get('p2_spu', 0)
                        } for k in sorted_keys]
                        
                        df = pd.DataFrame(rows)
                        
                        if len(df) < FETCH_LEN:
                            padding = pd.DataFrame([{k: 0 for k in df.columns}] * (FETCH_LEN - len(df)))
                            df = pd.concat([padding, df], ignore_index=True)
                            
                        # Standardize inputs to floating point representation safely
                        df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0.0)
                        
                        # =========================================================================
                        # SMOOTHED OPERATIONAL ENVELOPE GATES
                        # Evaluated on a 3-step running median of Flow 1 to filter out noise.
                        # Removing the pressure constraint ensures leak drops do not kill the loop.
                        # =========================================================================
                        smoothed_f1 = float(df_numeric['Flow_1_LPM'].tail(3).median())
                        is_pump_running = smoothed_f1 > 0.15
                        
                        if not is_pump_running:
                            st.session_state['priming_start_time'] = None
                            prob = 0.0
                            raw_pred = 0
                            system_log_status = "System Idle"
                        else:
                            if st.session_state['priming_start_time'] is None:
                                st.session_state['priming_start_time'] = time.time()
                                
                            seconds_since_startup = time.time() - st.session_state['priming_start_time']
                            
                            if seconds_since_startup < 15.0:
                                prob = 0.0
                                raw_pred = 0
                                system_log_status = "Priming Core"
                            else:
                                # Compute features and run model forward inference
                                features_df = create_scale_invariant_features(df_numeric)
                                sequence_matrix = features_df.values
                                input_tensor = torch.tensor(sequence_matrix, dtype=torch.float32).unsqueeze(0)
                                
                                with torch.no_grad():
                                    logits = model(input_tensor)
                                    prob = torch.sigmoid(logits).item()
                                    
                                # Balanced threshold boundary mapping matching training evaluation parameters
                                raw_pred = 1 if prob > 0.55 else 0
                                system_log_status = "Active"

                        # Temporal Stabilization Queue (4 out of 6 confirmation frames)
                        prediction_history.append(raw_pred)
                        if len(prediction_history) > 6: prediction_history.pop(0)
                        stable_pred = 1 if sum(prediction_history) >= 4 else 0

                        db.reference(f'sensor_readings/{latest_key}/label').set(stable_pred)
                        
                        if stable_pred == 1 and last_notified_state == 0:
                            send_leak_notification()
                            last_notified_state = 1
                        elif stable_pred == 0 and last_notified_state == 1:
                            send_clear_notification()
                            last_notified_state = 0

                        # Update layout UI display elements
                        f1_metric.metric("Flow 1", f"{float(latest_val.get('f1_lmin', 0)):.2f} L/min")
                        f2_metric.metric("Flow 2", f"{float(latest_val.get('f2_lmin', 0)):.2f} L/min")
                        
                        if stable_pred == 1:
                            status_placeholder.error("🚨 LEAK DETECTED!")
                        else:
                            status_placeholder.success(f"✅ System Secure ({system_log_status})")

                        logs.insert(0, f"[{latest_key}] Prob: {prob:.2%} -> Mode: {system_log_status} -> Alert: {'LEAK' if stable_pred else 'Normal'}")
                        with log_placeholder: st.code("\n".join(logs[:5]))
                        
                        last_processed_key = latest_key
                        last_sync_time.info(f"Last Sync: {latest_key}")

                if time.time() - last_update_wall_time > OFFLINE_TIMEOUT:
                    status_placeholder.warning("📡 ESP32 Offline - Monitoring Paused")
                    f1_metric.metric("Flow 1", "0.00 L/min (Off)")
                    f2_metric.metric("Flow 2", "0.00 L/min (Off)")
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Deployment Loop Exception: {str(e)}")
                time.sleep(2)