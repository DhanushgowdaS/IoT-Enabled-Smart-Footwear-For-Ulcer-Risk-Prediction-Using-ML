import pandas as pd
import requests
import streamlit as st
from datetime import datetime

API_BASE = "https://iot-enabled-smart-footwear-for-ulcer.onrender.com"
DATA_API = f"{API_BASE}/data"
CSV_API = f"{API_BASE}/download_csv"

st.set_page_config(
    page_title="Smart Footwear Dashboard",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Smart Footwear for Early Ulcer Detection")
st.caption("AI Powered IoT Monitoring Dashboard")

st.write("**Server:**", API_BASE)
st.write(datetime.now().strftime("%d %b %Y %H:%M:%S"))

if st.button("🔄 Refresh"):
    st.rerun()

try:
    r = requests.get(DATA_API, timeout=10)
    r.raise_for_status()
    data = r.json()

    if not data:
        st.warning("Waiting for sensor data...")
        st.stop()

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    latest = df.iloc[-1]

    a, b, c, d, e = st.columns(5)
    a.metric("FSR1", f"{latest['fsr1']:.0f}")
    b.metric("FSR2", f"{latest['fsr2']:.0f}")
    c.metric("FSR3", f"{latest['fsr3']:.0f}")
    d.metric("FSR4", f"{latest['fsr4']:.0f}")
    e.metric("Temperature", f"{latest['temp1']:.2f} °C")

    a, b, c, d = st.columns(4)
    a.metric("Average", f"{latest['avg_pressure']:.2f}")
    b.metric("Maximum", f"{latest['max_pressure']:.2f}")
    c.metric("Scenario", latest["scenario"])
    d.metric("Ulcer Risk", latest["ulcer_risk"])

    st.subheader("Pressure")
    st.line_chart(
        df.set_index("timestamp")[["fsr1", "fsr2", "fsr3", "fsr4"]],
        use_container_width=True
    )

    st.subheader("Temperature")
    st.line_chart(
        df.set_index("timestamp")[["temp1"]],
        use_container_width=True
    )

    st.subheader("Machine Learning Result")
    a, b, c = st.columns(3)
    a.metric("Healthy Match", f"{latest['healthy_match_percent']:.1f}%")
    b.metric("Mismatch", f"{latest['mismatch_percent']:.1f}%")
    c.metric("Ulcer Risk", latest["ulcer_risk"])

    risk = str(latest["ulcer_risk"]).lower()

    if risk == "safe":
        st.success(latest["ulcer_risk"])
    elif risk == "low risk":
        st.info(latest["ulcer_risk"])
    elif risk == "medium risk":
        st.warning(latest["ulcer_risk"])
    else:
        st.error(latest["ulcer_risk"])

    df["Time"] = df["timestamp"].dt.strftime("%H:%M:%S")

    table = df[
        [
            "Time",
            "scenario",
            "ulcer_risk",
            "fsr1",
            "fsr2",
            "fsr3",
            "fsr4",
            "temp1",
            "avg_pressure",
            "max_pressure",
            "healthy_match_percent",
            "mismatch_percent",
        ]
    ].tail(20)

    table = table.rename(
        columns={
            "scenario": "Scenario",
            "ulcer_risk": "Ulcer Risk",
            "fsr1": "FSR1",
            "fsr2": "FSR2",
            "fsr3": "FSR3",
            "fsr4": "FSR4",
            "temp1": "Temperature",
            "avg_pressure": "Average Pressure",
            "max_pressure": "Maximum Pressure",
            "healthy_match_percent": "Healthy Match %",
            "mismatch_percent": "Mismatch %",
        }
    )

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True
    )

    csv = requests.get(CSV_API, timeout=10).content
    st.download_button(
        "Download CSV",
        csv,
        file_name="sensor_data.csv",
        mime="text/csv"
    )

except requests.RequestException as e:
    st.error(f"Connection failed: {e}")
except Exception as e:
    st.error(str(e))
