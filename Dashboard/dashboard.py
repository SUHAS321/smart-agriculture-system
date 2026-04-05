import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

API_URL = "https://985o0lks84.execute-api.eu-north-1.amazonaws.com/reading"  # paste your invoke URL here

st.set_page_config(page_title="Smart Farm Monitor", layout="wide")
st.title("Smart Farm Monitor")

auto_refresh = st.sidebar.checkbox("Auto refresh every 30s", value=True)
farm_id      = st.sidebar.text_input("Farm ID", value="FARM_001")
limit        = st.sidebar.slider("Records to show", 5, 50, 20)

def fetch_data():
    try:
        r = requests.get(API_URL, params={"farm_id": farm_id, "limit": limit})
        data = r.json()
        df = pd.DataFrame(data)
        df['Timestamp']     = pd.to_datetime(df['Timestamp'])
        df['temperature']   = df['temperature'].astype(float)
        df['humidity']      = df['humidity'].astype(float)
        df['soil_moisture'] = df['soil_moisture'].astype(float)
        return df.sort_values('Timestamp')
    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

df = fetch_data()

if not df.empty:
    latest = df.iloc[-1]

    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Temperature", f"{latest['temperature']}°C")
    col2.metric("Humidity",    f"{latest['humidity']}%")

    soil = latest['soil_moisture']
    col3.metric("Soil Moisture", f"{soil}%",
                delta="LOW - Pump ON" if soil < 30 else "Normal")

    if soil < 30:
        st.error("DROUGHT ALERT - Soil moisture is critically low!")

    # Charts
    st.subheader("Temperature trend")
    st.plotly_chart(
        px.line(df, x='Timestamp', y='temperature', markers=True),
        use_container_width=True
    )

    st.subheader("Soil moisture trend")
    st.plotly_chart(
        px.line(df, x='Timestamp', y='soil_moisture', markers=True),
        use_container_width=True
    )

    st.subheader("Humidity trend")
    st.plotly_chart(
        px.line(df, x='Timestamp', y='humidity', markers=True),
        use_container_width=True
    )

    st.subheader("Raw data")
    st.dataframe(df.sort_values('Timestamp', ascending=False))

else:
    st.warning("No data yet — make sure Wokwi and bridge.py are running")

if auto_refresh:
    time.sleep(30)
    st.rerun()
