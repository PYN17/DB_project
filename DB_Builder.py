import psycopg2
import pandas as pd

import psycopg2
import pandas as pd

#database connection
conn = psycopg2.connect(
    dbname="satdata",
    user="pyn",
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

#pandas dtype to swl
def map_dtype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "TIMESTAMP"
    else:
        return "TEXT"


for file, table in csv_to_table.items():
    df = pd.read_csv(f"csv_data/{file}")
    df.columns = [c.strip().lower() for c in df.columns]  # normalize column names

    # convert dtypes
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            continue

    #create table if not present
    col_defs = ", ".join(f"{col} {map_dtype(df[col])}" for col in df.columns)
    create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({col_defs});"
    cursor.execute(create_sql)

    #insert data
    cols = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    insert_sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_sql, row)

    print(f"✓ Loaded {file} into {table}")

conn.commit()
cursor.close()
conn.close()

