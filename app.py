import os

import pandas as pd
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="Smart Footwear Dashboard", layout="wide")
st_autorefresh(interval=1000, key="live_dashboard")

st.title("🩺 Smart Footwear — Ulcer Risk Monitoring")

left, right = st.columns([1, 1])
with left:
    if st.button("🔄 Refresh Live Data"):
        st.rerun()
with right:
    st.write(f"API: `{API_URL}`")

try:
    response = requests.get(f"{API_URL}/data", timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data:
        st.info("Waiting for sensor data...")
    else:
        df = pd.DataFrame(data)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pressure Analysis")
            st.line_chart(df[["fsr1", "fsr2", "fsr3", "fsr4"]])
        with col2:
            st.subheader("Temperature")
            st.line_chart(df[["temp1"]])

        latest = df.iloc[0]
        st.subheader("Latest ML Result")
        a, b, c = st.columns(3)
        a.metric("Healthy Match", f"{latest['healthy_match_percent']:.1f}%")
        b.metric("Mismatch", f"{latest['mismatch_percent']:.1f}%")
        c.metric("Ulcer Risk", str(latest["ulcer_risk"]))

        st.subheader("Latest Entries & Status")
        table = df.head(20).copy()
        table.insert(0, "No.", range(1, len(table) + 1))
        table = table.rename(columns={
            "timestamp": "Time",
            "scenario": "Scenario",
            "fsr1": "FSR1",
            "fsr2": "FSR2",
            "fsr3": "FSR3",
            "fsr4": "FSR4",
            "temp1": "Temperature",
            "healthy_match_percent": "Healthy Match %",
            "mismatch_percent": "Mismatch %",
            "ulcer_risk": "Ulcer Risk",
        })

        st.dataframe(
            table[[
                "No.", "Time", "Scenario", "FSR1", "FSR2", "FSR3", "FSR4",
                "Temperature", "Healthy Match %", "Mismatch %", "Ulcer Risk"
            ]],
            use_container_width=True,
            hide_index=True,
        )
except requests.RequestException as exc:
    st.error(f"Connection failed: {exc}")
except Exception as exc:
    st.error(f"Dashboard error: {exc}")
