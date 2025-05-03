from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

DATABASE_URL = "postgresql://isaac:orphic@localhost:5433/FinalProject"
engine = create_engine(DATABASE_URL)

app = FastAPI()

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

@app.get("/uhi-data")
def get_uhi_data(location: str = Query(...), start_date: str = Query(...), end_date: str = Query(...)):
    try:
        query = text("""
            SELECT h.date, h.uhi, h.surface_temp, h.air_temp
            FROM heat_island h
            JOIN location l ON h.location_id = l.location_id
            WHERE l.name = :location AND h.date BETWEEN :start AND :end
            ORDER BY h.date
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {"location": location, "start": start_date, "end": end_date})
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

@app.post("/add-location")
def add_location(name: str = Query(...), latitude: float = Query(...), longitude: float = Query(...), pop_density: float = Query(...), elevation: float = Query(...)):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(location_id) FROM location"))
            max_id = result.scalar() or 0
            new_id = max_id + 1

            conn.execute(text("""
                INSERT INTO location (location_id, name, latitude, longitude, pop_density, elevation)
                VALUES (:id, :name, :latitude, :longitude, :pop_density, :elevation)
            """), {
                "id": new_id,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "pop_density": pop_density,
                "elevation": elevation
            })
            conn.commit()
        return {"message": "Location added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-location")
def delete_location(name: str = Query(...)):
    try:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM location WHERE name = :name"), {"name": name})
            conn.commit()
        return {"message": "Location deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

