import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from generate_data import *

st.set_page_config(
    page_title="Real-Time OEE Dashboard",
    layout="wide",
)

st.title("30 Day Real-Time OEE Production Dashboard")


def calculate_oee_metrics(df):
    """Calculate Availability, Performance, Quality, and OEE."""
    scheduled_time = 420  # minutes per shift

    optimal_cycle_time = (
        df['Average_Cycle_Time'].mean() - df['Average_Cycle_Time'].std()
    )

    availability = (scheduled_time - df['Downtime_Total']) / scheduled_time
    performance = (optimal_cycle_time * df['Production_Volume']) / scheduled_time
    quality = (
        (df['Production_Volume'] - df['Defects_Total']) /
        df['Production_Volume'].replace(0, np.nan)
    )

    df = df.copy()
    df['Availability'] = availability
    df['Performance'] = performance
    df['Quality'] = quality
    df['OEE'] = availability * performance * quality

    return df


def oee_subplots(df):
    """Create OEE subplots for Streamlit."""
    fig, axes = plt.subplots(4, 1, figsize=(14,10), sharex=True)

    axes[3].plot(df['Date'], df['Availability'], marker='o')
    axes[3].set_ylabel('Availability')
    axes[3].grid(True)
    axes[3].legend([f"Availability (Avg: {df['Availability'].mean():.2%})"])

    axes[1].plot(df['Date'], df['Performance'], marker='o')
    axes[1].set_ylabel('Performance')
    axes[1].grid(True)
    axes[1].legend([f"Performance (Avg: {df['Performance'].mean():.2%})"])

    axes[2].plot(df['Date'], df['Quality'], marker='o')
    axes[2].set_ylabel('Quality')
    axes[2].grid(True)
    axes[2].legend([f"Quality (Avg: {df['Quality'].mean():.2%})"])

    axes[0].plot(df['Date'], df['OEE'], marker='o')
    axes[0].set_ylabel('OEE')
    axes[0].set_xlabel('Date')
    axes[0].grid(True)
    axes[0].legend([f"OEE (Avg: {df['OEE'].mean():.2%})"])

    for ax in axes:
        ax.tick_params(labelsize=8)
        ax.set_ylabel(ax.get_ylabel(), fontsize=9)

    fig.suptitle(f"OEE Metrics – Line {df['Line'].iloc[0]}")
    fig.tight_layout()
    plt.xticks(rotation=30)
    return fig


def simulate_new_row(df):
    """Simulate incoming production data (real-time update)."""
    new_row = df.iloc[-1].copy()
    new_row['Date'] = pd.to_datetime(new_row['Date']) + pd.Timedelta(days=1)

    new_row['Production_Volume'] = max(0, new_row['Production_Volume'] + np.random.randint(-15, 15))
    new_row['Defects_Total'] = max(0, new_row['Defects_Total'] + np.random.randint(-3, 3))
    new_row['Downtime_Total'] = max(0, new_row['Downtime_Total'] + np.random.randint(-20, 20))
    new_row['Average_Cycle_Time'] = max(0.1, new_row['Average_Cycle_Time'] + np.random.uniform(-0.15, 0.15))

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Remove oldest entry

    return df.iloc[1:]

# ---------------------------
if "oee_df" not in st.session_state:
    dates = pd.date_range(end=pd.Timestamp.today(), periods=60)
    st.session_state.oee_df = pd.DataFrame({
        'Date': dates,
        'Line': ['A'] * len(dates),
        'Production_Volume': np.random.randint(80, 120, size=len(dates)),
        'Defects_Total': np.random.randint(0, 5, size=len(dates)),
        'Downtime_Total': np.random.randint(10, 90, size=len(dates)),
        'Average_Cycle_Time': np.random.uniform(1.5, 2.5, size=len(dates)),
    })

# ---------------------------
refresh_rate = 1
metrics_container_current = st.empty()
metrics_container = st.empty()
chart_container = st.empty()

while True:
    df = st.session_state.oee_df


    df = simulate_new_row(df)
    st.session_state.oee_df = df

    df['Date'] = pd.to_datetime(df['Date'])

    # Last 30 days only
    df_30 = df[df['Date'] >= df['Date'].max() - pd.Timedelta(days=30)]
    df_30 = calculate_oee_metrics(df_30)
    with metrics_container_current:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Availability", f"{df_30['Availability'].iloc[-1]:.2%}")
        col2.metric("Current Performance", f"{df_30['Performance'].iloc[-1]:.2%}")
        col3.metric("Current Quality", f"{df_30['Quality'].iloc[-1]:.2%}")
        col4.metric("Current OEE", f"{df_30['OEE'].iloc[-1]:.2%}")
    
    with metrics_container:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Availability", f"{df_30['Availability'].mean():.2%}")
        col2.metric("Avg Performance", f"{df_30['Performance'].mean():.2%}")
        col3.metric("Avg Quality", f"{df_30['Quality'].mean():.2%}")
        col4.metric("Avg OEE", f"{df_30['OEE'].mean():.2%}")

    fig = oee_subplots(df_30)
    with chart_container:
        st.pyplot(fig)

    time.sleep(refresh_rate)
