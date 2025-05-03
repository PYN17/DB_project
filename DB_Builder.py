import psycopg2
import pandas as pd
from getpass import getpass

#get input from user
username = input("Enter your PostgreSQL username: ")
password = getpass("Enter your PostgreSQL password: ")
new_db_name = input("Enter the name of the new database to create: ")

#connect to default postgres
conn_init = psycopg2.connect(
    dbname="postgres",
    user=username,
    password=password,
    host="localhost",
    port=5432
)
#create new database
conn_init.autocommit = True
cur_init = conn_init.cursor()
cur_init.execute(f"DROP DATABASE IF EXISTS {new_db_name};")
cur_init.execute(f"CREATE DATABASE {new_db_name};")
cur_init.close()
conn_init.close()

#Database connection
conn = psycopg2.connect(
    dbname=new_db_name,
    user=username,
    password=password,
    host="localhost",
    port=5432
)
cursor = conn.cursor()

csv_to_table = {
    "location.csv": "location",
    "satellite.csv": "satellite",
    "weather_station.csv": "weather_station",
    "urban_feature.csv": "urban_feature",
    "heat_island.csv": "heat_island",
    "observation.csv": "observation",
    "air_quality.csv": "air_quality",
    "weather_data.csv": "weather_data"
}

dtype_map = {
    "heat_island": {
        "effect_id": "INTEGER",
        "location_id": "INTEGER",
        "date": "DATE",
        "UHI": "NUMERIC",
        "surface_tmp": "NUMERIC",
        "vege_index": "NUMERIC",
        "air_temp": "NUMERIC"
    },
    "air_quality": {
        "aq_id": "INTEGER",
        "location_id": "INTEGER",
        "observation_date": "TIMESTAMP WITHOUT TIME ZONE",
        "pm2_5": "NUMERIC",
        "pm10": "NUMERIC",
        "co": "NUMERIC",
        "no2": "NUMERIC",
        "o3": "NUMERIC"
    },
    "observation": {
        "observation_id": "INTEGER",
        "satellite_id": "INTEGER",
        "location_id": "INTEGER",
        "timestamp": "TIMESTAMP WITHOUT TIME ZONE",
        "latitude": "NUMERIC",
        "longitude": "NUMERIC",
        "temperature": "NUMERIC",
        "lst": "NUMERIC",
        "ndvi": "NUMERIC",
        "emission": "NUMERIC"
    },
    "location": {
        "location_id": "INTEGER",
        "name": "character varying(255)",
        "latitude": "NUMERIC",
        "longitude": "NUMERIC",
        "elevation": "NUMERIC",
        "pop_density": "NUMERIC"
    },
    "weather_station": {
        "station_id": "INTEGER",
        "name": "character varying(255)",
        "latitude": "NUMERIC",
        "longitude": "NUMERIC"
    },
    "urban_feature": {
        "feature_id": "INTEGER",
        "location_id": "INTEGER",
        "name": "character varying(255)",
        "type": "character varying(255)",
        "area": "NUMERIC"
    },
    "weather_data": {
        "weather_id": "INTEGER",
        "station_id": "INTEGER",
        "observation_date": "date",
        "temp": "NUMERIC",
        "humidity": "NUMERIC",
        "wind_speed": "NUMERIC",
        "precipitation": "NUMERIC"
    },
    "satellite": {
        "satellite_id": "INTEGER",
        "name": "character varying(255)",
        "type": "character varying(255)",
        "operator": "character varying(255)",
        "launch_date": "date"
    }
}

#Use manual typing from dtype_map
for file, table in csv_to_table.items():
    df = pd.read_csv(f"csv_data/{file}")
    df.columns = [c.strip().lower() for c in df.columns]  #normalize column names

    print(f"\n== {file} column types ==")
    print(df.dtypes)

    # Check if each column has a manual type defined in dtype_map
    if table in dtype_map:
        # Ensure all columns are accounted for in dtype_map
        for col in df.columns:
            if col not in dtype_map[table]:
                print(f"Warning: No data type mapping for {col} in table {table}")

    # Create table if not exists (using manual typing from dtype_map)
    col_defs = ", ".join(f"{col} {dtype_map[table].get(col, 'TEXT')}" for col in df.columns)
    create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({col_defs});"
    cursor.execute(create_sql)

    # Insert data
    cols = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_sql, row)

    print(f"✓ Loaded {file} into {table}")

conn.commit()
cursor.close()
conn.close()
