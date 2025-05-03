import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

API_URL = "http://127.0.0.1:8000"  # Backend FastAPI server

st.set_page_config(layout="wide")
st.title("Arizona Urban Heat Island (UHI) Dashboard")

# === Fetch locations from backend ===
try:
    locations = requests.get(f"{API_URL}/locations").json()
    st.write("Fetched locations:", locations)  # Debug line
except Exception as e:
    st.error(f"Error fetching locations: {e}")
    locations = []

# === Sidebar ===
st.sidebar.header("User Input")
location = st.sidebar.selectbox("Select a Location", options=locations)
date_range = st.sidebar.date_input("Select Date Range")

if isinstance(date_range, tuple) and len(date_range) == 2 and st.sidebar.button("Load Data"):
    start_date, end_date = date_range

    try:
        # --- UHI Data ---
        uhi = requests.get(f"{API_URL}/uhi-data", params={
            "location": location,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }).json()
        uhi_df = pd.DataFrame(uhi)

        # --- Observations ---
        obs = requests.get(f"{API_URL}/observations", params={
            "location": location,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }).json()
        obs_df = pd.DataFrame(obs)

        # --- Air Quality ---
        aq = requests.get(f"{API_URL}/air-quality", params={
            "location": location,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }).json()
        aq_df = pd.DataFrame(aq)

        # --- Weather ---
        weather = requests.get(f"{API_URL}/weather", params={
            "location": location,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }).json()
        weather_df = pd.DataFrame(weather)

        # === Visualizations ===
        st.subheader("📈 UHI Trend")
        fig1 = px.line(uhi_df, x="date", y=["surface_temp", "air_temp", "UHI"])
        st.plotly_chart(fig1)

        st.subheader("🛰 Satellite Observations")
        st.plotly_chart(px.scatter(obs_df, x="timestamp", y="temperature", color="satellite_name"))

        st.subheader("🌫 Air Quality")
        st.plotly_chart(px.line(aq_df, x="timestamp", y=["PM2_5", "NO2", "O3"]))

        st.subheader("🌦 Weather Data")
        st.dataframe(weather_df)

    except Exception as e:
        st.error(f"Error loading data: {e}")

else:
    st.info("⬅ Please select a location and date range, then click 'Load Data'.")


