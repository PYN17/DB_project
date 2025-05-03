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
    #st.write("Fetched locations:", locations)  # Debug line
except Exception as e:
    st.error(f"Error fetching locations: {e}")
    locations = []

import datetime

# === Sidebar ===
st.sidebar.header("User Input")
location = st.sidebar.selectbox("Select a Location", options=locations)

# Force date input to be a range
default_start = datetime.date(2023, 1, 1)
default_end = datetime.date(2023, 1, 10)
date_range = st.sidebar.date_input("Select Date Range", value=(default_start, default_end))

load_data = st.sidebar.button("Load Data")

if load_data:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range

        try:
            # --- UHI Data ---
            uhi = requests.get(f"{API_URL}/uhi-data", params={
                "location": location,
                "start_date": str(start_date),
                "end_date": str(end_date)
            }).json()
            
            uhi_df = pd.DataFrame(uhi)
            st.write("Raw UHI response:", uhi)
            st.write("UHI DataFrame preview:", uhi_df)


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
            st.subheader("📈 UHI Effect Over Time")
            required_cols = {"date", "surface_temp", "air_temp", "uhi"}
            if not uhi_df.empty and required_cols.issubset(uhi_df.columns):
                uhi_df = uhi_df.dropna(subset=required_cols)
                if not uhi_df.empty:
                    fig = px.line(
                        uhi_df,
                        x="date",
                        y=["surface_temp", "air_temp", "uhi"],
                        labels={"value": "Temperature (°C)", "variable": "Metric"},
                        title="Surface Temp, Air Temp, and UHI Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("UHI data exists but contains missing values.")
            else:
                st.warning("No valid UHI data found for the selected location and date range.")

        except Exception as e:
            st.error(f"Error loading data: {e}")
    else:
        st.warning("Please select both a start and end date to load data.")
