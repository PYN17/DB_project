import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def query_db(sql, params=None):
    conn = psycopg2.connect(
        dbname="satdata",
        user="pyn",
        host="localhost",
        port=5432
    )
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

# PAGE CONFIG 
st.set_page_config(layout="wide")
st.title("🌆 Arizona Urban Heat Island (UHI) Dashboard")

# MOCK DATA
locations = ["Phoenix", "Tucson", "Yuma", "Flagstaff"]

# SIDEBAR INPUTS
st.sidebar.header("User Input")
location = st.sidebar.selectbox("Select a Location", options=locations)

date_range = st.sidebar.date_input("Select Date Range", [])
if len(date_range) == 2:
    start_date = date_range[0]
    end_date = date_range[1]
else:
    start_date = end_date = None

# === SIMULATED DATA ===
if st.sidebar.button("Load Data") and start_date and end_date:

    # Sample UHI data 
    uhi_df = pd.DataFrame({
        "date": pd.date_range(start=start_date, end=end_date),
        "surface_temp": [32 + i*0.2 for i in range((end_date - start_date).days + 1)],
        "air_temp": [30 + i*0.1 for i in range((end_date - start_date).days + 1)],
        "UHI": [2 + 0.1*i for i in range((end_date - start_date).days + 1)]
    })

    # Sample Observation data 
    obs_df = pd.DataFrame({
        "timestamp": pd.date_range(start=start_date, periods=10),
        "temperature": [28 + i for i in range(10)],
        "satellite_id": ["MODIS"] * 10
    })

    # Sample Air Quality 
    aq_df = pd.DataFrame({
        "timestamp": pd.date_range(start=start_date, periods=10),
        "PM2_5": [12 + i for i in range(10)],
        "NO2": [5 + i for i in range(10)],
        "O3": [18 + i for i in range(10)]
    })

    # Sample Weather Data 
    weather_df = pd.DataFrame({
        "observation_date": pd.date_range(start=start_date, periods=5),
        "temp": [30 + i for i in range(5)],
        "humidity": [40 + i for i in range(5)],
        "wind_speed": [5 + i for i in range(5)],
        "precipitation": [0, 1, 0, 0, 2]
    })

    # UHI Trends
    st.subheader("📈 UHI Trend")
    fig1 = px.line(uhi_df, x="date", y=["surface_temp", "air_temp", "UHI"], title="Surface vs Air Temp and UHI")
    st.plotly_chart(fig1)

    # Satellite Observations
    st.subheader("🛰 Satellite Observations")
    fig2 = px.scatter(obs_df, x="timestamp", y="temperature", color="satellite_id", title="LST Observations Over Time")
    st.plotly_chart(fig2)

    # Air Quality 
    st.subheader("🌫 Air Quality Over Time")
    fig3 = px.line(aq_df, x="timestamp", y=["PM2_5", "NO2", "O3"], title="Air Pollution Metrics")
    st.plotly_chart(fig3)

    # Weather Summary 
    st.subheader("🌦 Weather Summary")
    st.dataframe(weather_df)

else:
    st.info("⬅ Please select a location and date range, then click 'Load Data'.")

