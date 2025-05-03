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


#Query definition
uhi_query = """
    SELECT date AS date, surface_temp, air_temp, (surface_temp - air_temp) AS UHI
    FROM heat_island
    WHERE location = %s AND date BETWEEN %s AND %s
    ORDER BY odate
"""

obs_query = """
    SELECT timestamp, temperature, satellite_id
    FROM observation
    WHERE location = %s AND timestamp BETWEEN %s AND %s
    ORDER BY timestamp
"""
aq_query = """
    SELECT timestamp, PM2_5, NO2, O3
    FROM air_quality
    WHERE location = %s AND timestamp BETWEEN %s AND %s
    ORDER BY timestamp
"""
weather_query = """
    SELECT observation_date, temp, humidity, wind_speed, precipitation
    FROM weather_data
    WHERE location = %s AND observation_date BETWEEN %s AND %s
    ORDER BY observation_date
"""

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

if st.sidebar.button("Load Data") and start_date and end_date:

    #handle time stamp conversion
    start_date = datetime.combine(date_range[0], datetime.min.time())
    end_date = datetime.combine(date_range[1], datetime.max.time())

    # Sample UHI data 
    uhi_df = query_db(uhi_query, (location, start_date, end_date))

    # Sample Observation data 
    obs_df = query_db(obs_query, (location, start_date, end_date))

    # Sample Air Quality 
    aq_df = query_db(aq_query, (location, start_date, end_date))

    # Sample Weather Data 
    weather_df = query_db(weather_query, (location, start_date, end_date))

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

