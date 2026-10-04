import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

API_BASE = "https://iot-enabled-smart-footwear-for-ulcer.onrender.com"
DATA_API = f"{API_BASE}/data"
LATEST_API = f"{API_BASE}/latest"
CSV_API = f"{API_BASE}/download_csv"

IST = ZoneInfo("Asia/Kolkata")

st.set_page_config(
    page_title="IoT-Enabled Smart Footwear",
    page_icon="🩺",
    layout="wide"
)

st_autorefresh(interval=5000, key="live_refresh")

st.markdown("""
<style>
.stApp {
    background: #0b0e16;
    color: #f4f7fb;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
h1 {
    font-size: 2.55rem !important;
    font-weight: 800 !important;
    color: #f4f7fb !important;
    letter-spacing: -0.5px;
}
h2, h3 {
    color: #f4f7fb !important;
}
[data-testid="stMetric"] {
    background: transparent;
}
.clock {
    color: #f3f5f9;
    font-size: 1rem;
    font-weight: 700;
}
.risk-box {
    background: #17324d;
    border-radius: 7px;
    padding: 22px 28px 20px 28px;
    margin: 18px 0 30px 0;
    border: 1px solid #244761;
}
.risk-title {
    color: #58aefc;
    font-size: 1.55rem;
    font-weight: 800;
    margin-bottom: 12px;
}
.risk-main {
    font-size: 1.45rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.risk-sub {
    color: #65a7df;
    font-size: 0.95rem;
    margin-bottom: 16px;
}
.risk-counts {
    font-size: 0.98rem;
    color: #58aefc;
    word-spacing: 3px;
}
.risk-dot-safe { color: #8ed244; }
.risk-dot-low { color: #ffd126; }
.risk-dot-medium { color: #ff9f17; }
.risk-dot-high { color: #ff4d4d; }
div[data-testid="stButton"] > button {
    border: 1px solid #364253;
    background: #101520;
    color: #f4f7fb;
    border-radius: 7px;
    font-weight: 700;
}
div[data-testid="stDownloadButton"] > button {
    background: #1976d2;
    color: white;
    border: 0;
    border-radius: 6px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.title("🩺 IoT-Enabled Smart Footwear for Foot Ulcer Risk Prediction Using Machine Learning")

top_left, top_right = st.columns([1, 1])

with top_left:
    if st.button("🔄 Refresh Live Data"):
        st.rerun()

with top_right:
    current_ist = datetime.now(IST)
    st.markdown(
        f'<div class="clock">◷ {current_ist.strftime("%d/%m/%Y %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

try:
    cache_buster = str(int(time.time()))

    request_headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    data_response = requests.get(
        DATA_API,
        params={"_t": cache_buster},
        headers=request_headers,
        timeout=15
    )
    data_response.raise_for_status()
    data = data_response.json()

    latest_response = requests.get(
        LATEST_API,
        params={"_t": cache_buster},
        headers=request_headers,
        timeout=15
    )
    latest_response.raise_for_status()
    latest_data = latest_response.json()

    if latest_data:
        if not data:
            data = [latest_data]
        else:
            latest_timestamp = latest_data.get("timestamp")
            data = [
                row for row in data
                if row.get("timestamp") != latest_timestamp
            ]
            data.append(latest_data)

    if not data:
        st.warning("Waiting for sensor data...")
        st.stop()

    df = pd.DataFrame(data)

    required_columns = [
        "timestamp",
        "scenario",
        "fsr1",
        "fsr2",
        "fsr3",
        "fsr4",
        "temp1",
        "avg_pressure",
        "max_pressure",
        "healthy_match_percent",
        "mismatch_percent",
        "ulcer_risk"
    ]

    missing_columns = [c for c in required_columns if c not in df.columns]

    if missing_columns:
        st.error(f"Missing API fields: {missing_columns}")
        st.stop()

    # Render stores backend timestamps in UTC. Display them in IST.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True
    )

    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

    if df.empty:
        st.warning("Waiting for valid sensor data...")
        st.stop()

    df["display_timestamp"] = df["timestamp"].dt.tz_convert(IST)

    latest = df.iloc[-1]
    cutoff = latest["timestamp"] - pd.Timedelta(minutes=10)
    recent = df[df["timestamp"] >= cutoff].copy()

    pressure_col, temp_col = st.columns(2)

    with pressure_col:
        st.subheader("Pressure Analysis")

        fig_pressure = go.Figure()

        pressure_colors = {
            "fsr1": "#7ec8ff",
            "fsr2": "#3f8cff",
            "fsr3": "#f3a5ae",
            "fsr4": "#ff4b4b",
        }

        for sensor, color in pressure_colors.items():
            fig_pressure.add_trace(
                go.Scatter(
                    x=recent["display_timestamp"],
                    y=recent[sensor],
                    mode="lines+markers",
                    name=sensor,
                    line=dict(color=color, width=2),
                    marker=dict(size=4),
                )
            )

        fig_pressure.update_layout(
            height=330,
            margin=dict(l=0, r=0, t=15, b=0),
            paper_bgcolor="#0b0e16",
            plot_bgcolor="#0b0e16",
            font=dict(color="#e9edf4"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.22,
                xanchor="left",
                x=0
            ),
            hovermode="x unified",
            xaxis=dict(
                showgrid=False,
                tickformat="%H:%M:%S",
                color="#d8dee8"
            ),
            yaxis=dict(
                title="Pressure Value",
                range=[0, 4095],
                gridcolor="#252b36",
                zeroline=False,
                color="#d8dee8"
            ),
        )

        st.plotly_chart(
            fig_pressure,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    with temp_col:
        st.subheader("Temperature")

        fig_temp = go.Figure()

        fig_temp.add_trace(
            go.Scatter(
                x=recent["display_timestamp"],
                y=recent["temp1"],
                mode="lines+markers",
                name="Temperature",
                line=dict(color="#b787ff", width=2),
                marker=dict(size=4),
            )
        )

        fig_temp.update_layout(
            height=330,
            margin=dict(l=0, r=0, t=15, b=0),
            paper_bgcolor="#0b0e16",
            plot_bgcolor="#0b0e16",
            font=dict(color="#e9edf4"),
            showlegend=False,
            hovermode="x unified",
            xaxis=dict(
                showgrid=False,
                tickformat="%H:%M:%S",
                color="#d8dee8"
            ),
            yaxis=dict(
                title="Temperature (°C)",
                gridcolor="#252b36",
                zeroline=False,
                color="#d8dee8"
            ),
        )

        st.plotly_chart(
            fig_temp,
            use_container_width=True,
            config={"displayModeBar": False}
        )

    risk_order = ["High Risk", "Medium Risk", "Low Risk", "Safe"]
    counts = recent["ulcer_risk"].value_counts()

    risk_counts = {
        risk: int(counts.get(risk, 0))
        for risk in risk_order
    }

    highest_count = max(risk_counts.values())

    tied = [
        risk for risk in risk_order
        if risk_counts[risk] == highest_count
    ]

    recent_risks = recent["ulcer_risk"].astype(str).tolist()

    overall_risk = next(
        (risk for risk in reversed(recent_risks) if risk in tied),
        "Safe"
    )

    risk_styles = {
        "Safe": ("🟢", "risk-dot-safe"),
        "Low Risk": ("🟡", "risk-dot-low"),
        "Medium Risk": ("🟠", "risk-dot-medium"),
        "High Risk": ("🔴", "risk-dot-high"),
    }

    dot, dot_class = risk_styles.get(
        overall_risk,
        ("🟢", "risk-dot-safe")
    )

    st.markdown(
        f"""
        <div class="risk-box">
            <div class="risk-title">Overall Risk Assessment</div>
            <div class="risk-main">
                <span class="{dot_class}">{dot}</span>&nbsp; {overall_risk}
            </div>
            <div class="risk-sub">
                Based on Readings from the Last 10 Minutes
            </div>
            <div class="risk-counts">
                🔴 High Risk : {risk_counts["High Risk"]}&nbsp;&nbsp;
                🟠 Medium Risk : {risk_counts["Medium Risk"]}&nbsp;&nbsp;
                🟡 Low Risk : {risk_counts["Low Risk"]}&nbsp;&nbsp;
                🟢 Safe : {risk_counts["Safe"]}
            </div>
            <div class="risk-sub" style="margin-top:12px;margin-bottom:0;">
                Total Readings Analysed: {len(recent)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Latest Entries & Status")

    table = df.tail(20).sort_values(
        "timestamp",
        ascending=False
    ).copy()

    table.insert(0, "No.", range(1, len(table) + 1))

    table["timestamp"] = table["display_timestamp"].dt.strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )

    status_icons = {
        "Safe": "🟢 Safe",
        "Low Risk": "🟡 Low Risk",
        "Medium Risk": "🟠 Medium Risk",
        "High Risk": "🔴 High Risk",
    }

    table["Display_Status"] = (
        table["ulcer_risk"]
        .map(status_icons)
        .fillna(table["ulcer_risk"])
    )

    table = table[
        [
            "No.",
            "timestamp",
            "Display_Status",
            "fsr1",
            "fsr2",
            "fsr3",
            "fsr4",
            "temp1",
        ]
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "No.": st.column_config.NumberColumn(
                "No.",
                width="small"
            ),
            "timestamp": st.column_config.TextColumn(
                "timestamp"
            ),
            "Display_Status": st.column_config.TextColumn(
                "Display_Status"
            ),
            "fsr1": st.column_config.NumberColumn(
                "fsr1",
                format="%.3f"
            ),
            "fsr2": st.column_config.NumberColumn(
                "fsr2",
                format="%.3f"
            ),
            "fsr3": st.column_config.NumberColumn(
                "fsr3",
                format="%.3f"
            ),
            "fsr4": st.column_config.NumberColumn(
                "fsr4",
                format="%.3f"
            ),
            "temp1": st.column_config.NumberColumn(
                "temp1",
                format="%.4f"
            ),
        }
    )

    st.caption("Showing latest 20 readings")

    csv_response = requests.get(
        CSV_API,
        params={"_t": cache_buster},
        headers=request_headers,
        timeout=15
    )
    csv_response.raise_for_status()

    st.download_button(
        "⬇ Download Sensor Data (CSV)",
        csv_response.content,
        file_name="sensor_data.csv",
        mime="text/csv",
        use_container_width=False,
    )

except requests.RequestException as exc:
    st.error(f"Connection failed: {exc}")
except Exception as exc:
    st.error(f"Dashboard error: {exc}")
