"""
================================================================================
FLOWISE: DEFENSE PRESENTATION FEATURE VISUALIZATIONS
================================================================================
Generates high-resolution, publication-quality visualizations of raw sensor
signals and engineered features before, during, and after a leak event.

Perfect for inclusion in your FYP / Thesis Defense Presentation slides.
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set professional aesthetics for defense slides
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("tab10")

def compute_features(df, window_size=30):
    """Computes rolling features consistent with the training & real-time pipeline."""
    df = df.copy()
    
    # Raw Divergence
    df['flow_div_raw'] = df['F1_Lmin'] - df['F2_Lmin']
    df['pres_div_raw'] = df['P2_SPU'] - df['P1_SPU']
    
    # Flow Features
    df['Flow_Div_Norm'] = (df['flow_div_raw'] / 2.5).clip(0, 1)
    df['Flow_Div_Trend'] = df['flow_div_raw'].rolling(window=window_size, min_periods=1).mean()
    df['F1_Lmin_Norm'] = (df['F1_Lmin'] / 30.0).clip(0, 1)
    df['F2_Lmin_Norm'] = (df['F2_Lmin'] / 30.0).clip(0, 1)
    
    # Pressure Features
    df['Pres_Div_Norm'] = (df['pres_div_raw'] / 10.0).clip(-1, 1)
    df['Pres_Div_Trend'] = df['pres_div_raw'].rolling(window=window_size, min_periods=1).mean()
    df['P1_SPU_Norm'] = (df['P1_SPU'] / 1200.0).clip(0, 1)
    df['P2_SPU_Norm'] = (df['P2_SPU'] / 1200.0).clip(0, 1)
    
    return df

def plot_leak_dynamics(data_path, output_dir):
    """Generates a 3-panel figure showing raw signals vs engineered features."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and process data
    df = pd.read_csv(data_path)
    df = compute_features(df, window_size=10) # Using 10 for responsive visualization on sample data
    
    # Determine transition index where leak starts (Label goes 0 -> 1)
    leak_start_idx = df[df['Label'] == 1].index[0]
    time_s = np.arange(len(df)) * 2 # Assuming 2-second sampling interval
    leak_start_time = time_s[leak_start_idx]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    # ----------------------------------------------------
    # PANEL 1: Raw Flow Dynamics (Hydraulic Conservation)
    # ----------------------------------------------------
    ax1.plot(time_s, df['F1_Lmin'], lw=2.5, color='#2ecc71', label='Inlet Flow (F1)')
    ax1.plot(time_s, df['F2_Lmin'], lw=2.5, color='#e74c3c', label='Outlet Flow (F2)')
    
    ax1.axvline(x=leak_start_time, color='black', ls='--', lw=2, label='Leak Valve Opened')
    ax1.axvspan(0, leak_start_time, color='#2ecc71', alpha=0.1, label='Normal State')
    ax1.axvspan(leak_start_time, time_s[-1], color='#e74c3c', alpha=0.1, label='Leak State')
    
    ax1.set_ylabel('Flow Rate (L/min)', fontsize=12, fontweight='bold')
    ax1.set_title('Hydraulic Conservation & Divergence During Leak Event', fontsize=14, fontweight='bold', pad=10)
    ax1.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.9)
    ax1.grid(True, linestyle=':', alpha=0.6)
    
    # ----------------------------------------------------
    # PANEL 2: Engineered Flow Divergence Features
    # ----------------------------------------------------
    ax2.plot(time_s, df['flow_div_raw'], lw=2, color='#3498db', label='Flow Div Raw (F1 - F2)')
    ax2.plot(time_s, df['Flow_Div_Trend'], lw=3, color='#2980b9', ls='-', label='Flow Div Trend (Rolling Mean)')
    
    ax2.axvline(x=leak_start_time, color='black', ls='--', lw=2)
    ax2.axvspan(0, leak_start_time, color='#2ecc71', alpha=0.1)
    ax2.axvspan(leak_start_time, time_s[-1], color='#e74c3c', alpha=0.1)
    
    ax2.set_ylabel('Divergence (L/min)', fontsize=12, fontweight='bold')
    ax2.set_title('Feature Engineering: Flow Divergence Trend (XGBoost Primary Indicator)', fontsize=14, fontweight='bold', pad=10)
    ax2.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.9)
    ax2.grid(True, linestyle=':', alpha=0.6)
    
    # ----------------------------------------------------
    # PANEL 3: Pressure Dynamics & Trends
    # ----------------------------------------------------
    ax3.plot(time_s, df['P1_SPU'], lw=2, color='#9b59b6', label='P1 Pressure Sensor')
    ax3.plot(time_s, df['P2_SPU'], lw=2, color='#e67e22', label='P2 Pressure Sensor')
    
    ax3.axvline(x=leak_start_time, color='black', ls='--', lw=2)
    ax3.axvspan(0, leak_start_time, color='#2ecc71', alpha=0.1)
    ax3.axvspan(leak_start_time, time_s[-1], color='#e74c3c', alpha=0.1)
    
    ax3.set_xlabel('Elapsed Time (seconds)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Pressure (SPU)', fontsize=12, fontweight='bold')
    ax3.set_title('Pipeline Pressure Response Across Prototype Nodes', fontsize=14, fontweight='bold', pad=10)
    ax3.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.9)
    ax3.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'defense_feature_dynamics.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Generated defense feature visualization: {output_path}")

if __name__ == "__main__":
    # Define Kaggle environment paths
    eval_csv = "/kaggle/input/datasets/sarakhan24/evaldata/test_medium4.csv"
    out_dir = "/kaggle/working/"
    
    # Fallback to local test data if not running on Kaggle
    if not os.path.exists("/kaggle"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        eval_csv = os.path.join(base_dir, "../evaluation_data/test_medium4.csv")
        out_dir = os.path.join(base_dir, "../evaluation_results")
        
    if os.path.exists(eval_csv):
        plot_leak_dynamics(eval_csv, out_dir)
    else:
        print(f"❌ File not found: {eval_csv}")
