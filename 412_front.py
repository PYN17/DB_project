import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("Arizona Urban Heat Island (UHI) Dashboard")

# === Fetch locations from backend ===
try:
    locations = requests.get(f"{API_URL}/locations").json()
except Exception as e:
    st.error(f"Error fetching locations: {e}")
    locations = []

# === Sidebar ===
st.sidebar.header("User Input")
location = st.sidebar.selectbox("Select a Location", options=locations)

default_start = datetime.date(2023, 1, 1)
default_end = datetime.date(2023, 1, 1)
date_range = st.sidebar.date_input("Select Date Range", value=(default_start, default_end))
load_data = st.sidebar.button("Load Data")

st.sidebar.markdown("---")
st.sidebar.subheader("Edit Controls")

#Insert Location Form (with location_id)
with st.sidebar.form("insert_location"):
    st.markdown("**Insert New Location**")
    loc_id = st.number_input("Location ID", min_value=1, step=1)
    new_name = st.text_input("Name")
    new_lat = st.number_input("Latitude", format="%.6f")
    new_lon = st.number_input("Longitude", format="%.6f")
    new_pop = st.number_input("Population Density")
    new_elev = st.number_input("Elevation")
    insert_btn = st.form_submit_button("Add Location")
    if insert_btn:
        try:
            res = requests.post(
                f"{API_URL}/add-location",
                params={
                    "location_id": loc_id,
                    "name": new_name,
                    "latitude": new_lat,
                    "longitude": new_lon,
                    "pop_density": new_pop,
                    "elevation": new_elev,
                }
            )
            if res.status_code == 200:
                st.sidebar.success("Location added.")
                st.rerun()
            else:
                st.sidebar.error(res.json()["detail"])
        except Exception as e:
            st.sidebar.error(f"Insert failed: {e}")

#Delete Location
with st.sidebar.form("delete_location"):
    st.markdown("**Delete Existing Location**")
    del_name = st.selectbox("Location to delete", options=locations)
    del_btn = st.form_submit_button("Delete Location")
    if del_btn:
        try:
            res = requests.delete(f"{API_URL}/delete-location", params={"name": del_name})
            if res.status_code == 200:
                st.sidebar.success("Location deleted.")
                st.rerun()
            else:
                st.sidebar.error(res.json()["detail"])
        except Exception as e:
            st.sidebar.error(f"Delete failed: {e}")

# === Main Display ===
if load_data:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        try:
            response = requests.get(f"{API_URL}/location-coordinates", params={"location": location}).json()
            if "latitude" in response and "longitude" in response:
                coords = {"latitude": response["latitude"], "longitude": response["longitude"]}
                st.subheader("📍 Location of Weather Station")
                st.map(pd.DataFrame([coords], columns=["latitude", "longitude"]))
            else:
                st.warning("No coordinates found for this location.")
        except Exception as e:
            st.warning(f"Could not fetch coordinates: {e}")

        try:
            uhi = requests.get(f"{API_URL}/uhi-data", params={
                "location": location,
                "start_date": str(start_date),
                "end_date": str(end_date)
            }).json()
            uhi_df = pd.DataFrame(uhi)

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
            st.error(f"Error loading UHI data: {e}")
    else:
        st.warning("Please select both a start and end date to load data.")
