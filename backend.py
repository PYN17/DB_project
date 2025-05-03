from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

DATABASE_URL = "postgresql://isaac:orphic@localhost:5433/FinalProject"
engine = create_engine(DATABASE_URL)

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "UHI backend running"}

@app.get("/locations")
def get_locations():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM location ORDER BY name"))
            return [row[0] for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Query

@app.get("/uhi-data")
def get_uhi_data(
    location: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    try:
        query = text("""
            SELECT h.date, h.uhi, h.surface_temp, h.air_temp
            FROM heat_island h
            JOIN location l ON h.location_id = l.location_id
            WHERE l.name = :location
              AND h.date BETWEEN :start AND :end
            ORDER BY h.date
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {
                "location": location,
                "start": start_date,
                "end": end_date
            })
            rows = [dict(row._mapping) for row in result]
            return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/observations")
def get_observations(
    location: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    try:
        query = text("""
            SELECT o.timestamp, o.temperature, o.lst, o.ndvi, o.emission, s.name AS satellite_name
            FROM observation o
            JOIN location l ON o.location_id = l.location_id
            JOIN satellite s ON o.satellite_id = s.satellite_id
            WHERE l.name = :location
              AND o.timestamp BETWEEN :start AND :end
            ORDER BY o.timestamp
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {
                "location": location,
                "start": start_date,
                "end": end_date
            })
            return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/air-quality")
def get_air_quality(
    location: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    try:
        query = text("""
            SELECT aq.timestamp, aq.pm2_5, aq.pm10, aq.co, aq.no2, aq.o3
            FROM air_quality aq
            JOIN location l ON aq.location_id = l.location_id
            WHERE l.name = :location
              AND aq.timestamp BETWEEN :start AND :end
            ORDER BY aq.timestamp
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {
                "location": location,
                "start": start_date,
                "end": end_date
            })
            return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/weather")
def get_weather_data(
    location: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    try:
        query = text("""
            SELECT wd.observation_date, wd.temp, wd.humidity, wd.wind_speed, wd.precipitation
            FROM weather_data wd
            JOIN weather_station ws ON wd.station_id = ws.station_id
            JOIN location l ON ROUND(ws.latitude, 4) = ROUND(l.latitude, 4)
                            AND ROUND(ws.longitude, 4) = ROUND(l.longitude, 4)
            WHERE l.name = :location
              AND wd.observation_date BETWEEN :start AND :end
            ORDER BY wd.observation_date
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {
                "location": location,
                "start": start_date,
                "end": end_date
            })
            return [dict(row._mapping) for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/location-coordinates")
def get_coordinates(location: str = Query(...)):
    try:
        query = text("""
            SELECT latitude, longitude
            FROM location
            WHERE LOWER(name) = LOWER(:location)
            LIMIT 1
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {"location": location})
            row = result.fetchone()
            if row:
                return {"latitude": row[0], "longitude": row[1]}
            else:
                raise HTTPException(status_code=404, detail="Location not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

