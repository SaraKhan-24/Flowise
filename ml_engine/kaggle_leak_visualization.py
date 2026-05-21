import os
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt

# --- CONFIGURATION & PATHS ---
# Kaggle Input Paths (as requested)
KAGGLE_DATA_PATH = "/kaggle/input/datasets/sarakhan24/evaldata/test_medium3.csv"
KAGGLE_MODEL_PATH = "/kaggle/input/models/sarakhan24/leak-detection-model/other/default/1/xgb_leak_detector_hardware_finetuned.json"

# Local Fallbacks (for testing on your machine)
LOCAL_DATA_PATH = "../evaluation_data/test_medium3.csv"
LOCAL_MODEL_PATH = "../hf_space/xgb_leak_detector_hardware_finetuned.json" # check in hf_space or parent

# --- RESOLVING ENVIRONMENT PATHS ---
data_path = KAGGLE_DATA_PATH if os.path.exists(KAGGLE_DATA_PATH) else LOCAL_DATA_PATH
model_path = KAGGLE_MODEL_PATH if os.path.exists(KAGGLE_MODEL_PATH) else LOCAL_MODEL_PATH

# Verify paths exist
if not os.path.exists(data_path):
    # Try absolute path fallback if relative path failed locally
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "../evaluation_data/test_medium3.csv")
    model_path = os.path.join(base_dir, "../hf_space/xgb_leak_detector_hardware_finetuned.json")

print(f"Reading dataset from: {data_path}")
print(f"Loading model from: {model_path}")

# --- 1. LOAD DATA & MODEL ---
df = pd.read_csv(data_path)
model = xgb.XGBClassifier()
model.load_model(model_path)

# --- 2. FEATURE ENGINEERING (matches production pipeline) ---
WINDOW_SIZE = 30

def create_features(raw_df):
    f_df = raw_df.copy()
    
    # Map raw CSV columns to expected feature names
    f_df['Flow_1_LPM'] = f_df['F1_Lmin']
    f_df['Flow_2_LPM'] = f_df['F2_Lmin']
    f_df['Pressure_1_SPU'] = f_df['P1_SPU']
    f_df['Pressure_2_SPU'] = f_df['P2_SPU']
    
    # Mathematical features
    f_df['flow_div_raw'] = f_df['Flow_1_LPM'] - f_df['Flow_2_LPM']
    f_df.loc[f_df['flow_div_raw'].abs() < 0.3, 'flow_div_raw'] = 0
    
    f_df['Flow_Div_Norm'] = (f_df['flow_div_raw'] / 2.5).clip(0, 1)
    f_df['Flow_Div_Trend'] = f_df['flow_div_raw'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    f_df['F1_Lmin_Norm'] = (f_df['Flow_1_LPM'] / 30.0).clip(0, 1)
    f_df['F2_Lmin_Norm'] = (f_df['Flow_2_LPM'] / 30.0).clip(0, 1)
    
    f_df['pres_div_raw'] = f_df['Pressure_2_SPU'] - f_df['Pressure_1_SPU']
    f_df['Pres_Div_Norm'] = (f_df['pres_div_raw'] / 10.0).clip(-1, 1)
    f_df['Pres_Div_Trend'] = f_df['pres_div_raw'].rolling(window=WINDOW_SIZE, min_periods=1).mean()
    f_df['P1_SPU_Norm'] = (f_df['Pressure_1_SPU'] / 1200.0).clip(0, 1)
    f_df['P2_SPU_Norm'] = (f_df['Pressure_2_SPU'] / 1200.0).clip(0, 1)
    
    cols = ['F1_Lmin_Norm', 'F2_Lmin_Norm', 'Flow_Div_Norm', 'Flow_Div_Trend',
            'P1_SPU_Norm', 'P2_SPU_Norm', 'Pres_Div_Norm', 'Pres_Div_Trend']
    return f_df[cols].fillna(0)

# Generate features and predict
features = create_features(df)
df['Predicted'] = model.predict(features)

# Apply prediction smoothing (majority vote filter used in app.py)
prediction_history = []
smoothed_predictions = []
for p in df['Predicted']:
    prediction_history.append(p)
    if len(prediction_history) > 5:
        prediction_history.pop(0)
    # Require 3 out of 5 frames to trigger stable alert
    stable_pred = 1 if sum(prediction_history) >= 3 else 0
    smoothed_predictions.append(stable_pred)
df['Predicted_Smoothed'] = smoothed_predictions

# Calculate Total System Pressure (P1 + P2) and apply smoothing to filter pump noise
df['P_total_raw'] = df['P1_SPU'] + df['P2_SPU']
df['P_total_smooth'] = df['P_total_raw'].rolling(window=10, min_periods=1).mean()

# Calculate timestamps relative to start (sampling rate ~2s)
time_s = np.arange(len(df)) * 2

# Identify the index where the leak valve is manually opened (Label goes 0 -> 1)
leak_indices = df[df['Label'] == 1].index
leak_start_time = time_s[leak_indices[0]] if len(leak_indices) > 0 else 0

# --- CROP STARTUP TRANSIENT ---
# Skips the first 32 seconds to remove the initial pump-startup transient in the plot
# (Calculations are done on full data first to preserve historical rolling window memory)
CROP_START_SECS = 32
plot_mask = (time_s >= CROP_START_SECS)
time_plot = time_s[plot_mask]
df_plot = df.loc[plot_mask].copy()

# --- 3. GENERATE SLIDE-READY VISUALIZATION ---
# Using professional presentation aesthetics: deep slate theme colors
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 11), sharex=True)

# Colors matching your presentation theme
COLOR_INLET = '#008080'  # Teal
COLOR_OUTLET = '#FF4500' # Orange-Red
COLOR_LEAK_BG = '#FFCCCC' # Light red for leak zone
COLOR_PRED = '#007ACC'   # Deep Blue
COLOR_PRES_SMOOTH = '#8E44AD' # Deep Purple
COLOR_PRES_RAW = '#D2B4DE'    # Faded Lavender

# PANEL 1: Flow Divergence (AI Flow Leak Signature)
ax1.plot(time_plot, df_plot['F1_Lmin'], lw=3, color=COLOR_INLET, label='Inlet Flow (S1)')
ax1.plot(time_plot, df_plot['F2_Lmin'], lw=3, color=COLOR_OUTLET, label='Outlet Flow (S2)')

# Highlight Leak zone based on ground truth
if len(leak_indices) > 0:
    ax1.axvspan(leak_start_time, time_plot[-1], color=COLOR_LEAK_BG, alpha=0.3, label='Active Leak State')
    ax1.axvline(x=leak_start_time, color='#A9A9A9', ls='--', lw=1.5)

ax1.set_title('Flow Divergence (Hydraulic Loss Signature)', fontsize=14, fontweight='bold', pad=12)
ax1.set_ylabel('Flow Rate (L/min)', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95)
ax1.set_ylim(0, 4.0)

# PANEL 2: Pressure Response (Downstream Drop Signature)
ax2.plot(time_plot, df_plot['P_total_raw'], lw=1.5, color=COLOR_PRES_RAW, alpha=0.6, label='Raw System Pressure (P1 + P2)')
ax2.plot(time_plot, df_plot['P_total_smooth'], lw=3.5, color=COLOR_PRES_SMOOTH, label='Smoothed System Pressure (Noise-Filtered)')

if len(leak_indices) > 0:
    ax2.axvspan(leak_start_time, time_plot[-1], color=COLOR_LEAK_BG, alpha=0.3, label='Active Leak State')
    ax2.axvline(x=leak_start_time, color='#A9A9A9', ls='--', lw=1.5)

ax2.set_title('Total System Pressure Response (Drop & Noise Filtering)', fontsize=14, fontweight='bold', pad=12)
ax2.set_ylabel('Pressure (SPU)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95)

# PANEL 3: Model Prediction vs Ground Truth
# True label (filled step area)
ax3.fill_between(time_plot, df_plot['Label'], step="pre", alpha=0.15, color='#7F8C8D', label='True Leak State (Ground Truth)')
# Model prediction (step line)
ax3.step(time_plot, df_plot['Predicted_Smoothed'], where="pre", lw=3.5, color=COLOR_PRED, label='AI Model Verdict')

# Calculate Latency if leak is present
title_suffix = ""
if len(leak_indices) > 0:
    ax3.axvline(x=leak_start_time, color='#A9A9A9', ls='--', lw=1.5)
    
    # Calculate Latency (Time between true leak and first positive predicted label)
    predicted_leak_indices = df_plot[df_plot['Predicted_Smoothed'] == 1].index
    if len(predicted_leak_indices) > 0:
        pred_start_time = time_s[predicted_leak_indices[0]]
        latency = pred_start_time - leak_start_time
        title_suffix = f" (Detected in {latency}s)"

ax3.set_title(f'AI Model Verdict{title_suffix}', fontsize=14, fontweight='bold', pad=12)
ax3.set_ylabel('Status', fontsize=12, fontweight='bold')
ax3.set_xlabel('Elapsed Time (seconds)', fontsize=12, fontweight='bold')
ax3.set_yticks([0, 1])
ax3.set_yticklabels(['Normal', 'LEAK!'])
ax3.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.95)
ax3.set_ylim(-0.1, 1.2)

# Global layout styling
plt.tight_layout()

# Save output image
output_filename = "leak_detection_signature.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"🎉 Success! Generated slide visualization at: {os.path.abspath(output_filename)}")
