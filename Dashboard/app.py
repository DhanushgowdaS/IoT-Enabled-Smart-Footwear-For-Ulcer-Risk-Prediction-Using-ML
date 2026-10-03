from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import requests

API_URL = "https://ai-footwear-ulcer-detection.onrender.com"

st.set_page_config(
    page_title="Smart Footwear Dashboard",
    layout="wide"
)

# Auto refresh (every second)
st_autorefresh(interval=1000, key="live_dashboard")

st.title("🩺 Smart Footwear for Early Detection of Foot Ulcers")

# ---------------- REFRESH & LIVE TIME ----------------
left, right = st.columns([1, 1])

with left:
    if st.button("🔄 Refresh Live Data"):
        st.rerun()

with right:
    st.components.v1.html("""
    <div id="clock"
    style="
        text-align:right;
        font-size:18px;
        font-weight:bold;
        color:white;
    ">
    </div>

    <script>
    function updateClock() {
        const now = new Date();

        const date = now.toLocaleDateString('en-GB');
        const time = now.toLocaleTimeString();

        document.getElementById("clock").innerHTML =
            "🕒 " + date + " " + time;
    }

    updateClock();
    setInterval(updateClock, 1000);
    </script>
    """, height=35)

# ---------------- FETCH DATA ----------------
try:
    response = requests.get(f"{API_URL}/data", timeout=10)

    if response.status_code == 200:
        data = response.json()

        if data:

            df = pd.DataFrame(data)

            # ---------------- CHARTS ----------------
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Pressure Analysis")
                st.line_chart(df[["fsr1", "fsr2", "fsr3", "fsr4"]])

            with col2:
                st.subheader("Temperature")
                st.line_chart(df[["temp1"]])

            # ---------------- OVERALL RISK ASSESSMENT ----------------
            # Use the last 10 minutes of data (60 readings at 10-second intervals)
            last60 = df.head(60)

            counts = last60["prediction"].astype(str).str.lower().value_counts()

            high = counts.get("high risk", 0)
            medium = counts.get("medium risk", 0)
            low = counts.get("low risk", 0)
            safe = counts.get("safe", 0)

            if high >= max(medium, low, safe):
                overall = "🔴 High Risk"
            elif medium >= max(high, low, safe):
                overall = "🟠 Medium Risk"
            elif low >= max(high, medium, safe):
                overall = "🟡 Low Risk"
            else:
                overall = "🟢 Safe"

            st.info(f"""
### Overall Risk Assessment

{overall}

Based on Readings from the Last 10 Minutes

🔴 High Risk : {high}
🟠 Medium Risk : {medium}
🟡 Low Risk : {low}
🟢 Safe : {safe}
""")

            # ---------------- STATUS TABLE ----------------

            st.subheader("Latest Entries & Status")

            def add_emoji(val):
                val = str(val).lower()

                if "high" in val:
                    return "🔴 High Risk"
                elif "medium" in val:
                    return "🟠 Medium Risk"
                elif "low" in val:
                    return "🟡 Low Risk"
                elif "safe" in val:
                    return "🟢 Safe"
                else:
                    return str(val)

            # Convert prediction to colored status
            df["Display_Status"] = df["prediction"].apply(add_emoji)

            # Show only latest 20 readings
            table_df = df.head(20).copy()

            # Add serial number
            table_df.insert(0, "No.", range(1, len(table_df) + 1))

            # Columns to display
            cols = [
                "No.",
                "timestamp",
                "Display_Status",
                "fsr1",
                "fsr2",
                "fsr3",
                "fsr4",
                "temp1"
            ]

            st.dataframe(
                table_df[cols],
                use_container_width=True,
                hide_index=True
            )

        else:
            st.warning("Waiting for sensor data...")

    else:
        st.error(f"Backend returned error: {response.status_code}")

except Exception as e:
    st.error(f"Connection failed: {e}")
