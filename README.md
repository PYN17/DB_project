# 🌆 Arizona Urban Heat Island (UHI) Dashboard

A **Streamlit-based interactive dashboard** that visualizes and analyzes **Urban Heat Island (UHI) effects** across cities in Arizona.  
The dashboard integrates **satellite imagery, weather data, and air quality measurements** stored in a **PostgreSQL database**, providing actionable insights into urban temperature patterns.

---

## 🔧 Key Features

- **Dynamic Filtering:** Explore data by **location** and **date**.  
- **UHI Trend Visualizations:** Track how urban heat varies over time.  
- **Satellite Observations:** View spatial heat maps derived from satellite imagery.  
- **Air Quality Time-Series:** Analyze correlations between UHI effects and air pollutants.  
- **Weather Summaries:** Compare temperature, humidity, and other meteorological conditions with UHI intensity.  

---

## 🗃 Data Sources

Data is ingested from CSV files into PostgreSQL tables:

| File | Description |
|------|-------------|
| `location.csv` | City and coordinate metadata |
| `satellite.csv` | Satellite-derived heat measurements |
| `weather_station.csv` | Weather station locations and info |
| `urban_feature.csv` | Urban infrastructure and land cover features |
| `heat_island.csv` | Calculated UHI intensities |
| `observation.csv` | Observed temperature readings |
| `air_quality.csv` | Air pollution metrics |
| `weather_data.csv` | Historical meteorological data |

**Data Ingestion:** All CSVs are imported and processed via `upload.py`.

---

## 🛠 Technologies Used

- **Python 3.x**  
- **Streamlit** for interactive web dashboards  
- **Pandas & NumPy** for data manipulation  
- **PostgreSQL** for structured data storage  
- **Matplotlib / Seaborn / Plotly** for visualization  
- **FastAPI

---

## 🎯 Learning Outcomes

- Built an interactive data visualization pipeline from raw CSVs to dashboard.

- Learned database integration with PostgreSQL and Python.

- Gained hands-on experience in environmental data analytics and urban climate research.

---

## 📌 Future Enhancements

- Add real-time weather API integration.

- Include predictive modeling for future UHI scenarios.

- Implement geospatial heat maps using Folium or Plotly Maps.
