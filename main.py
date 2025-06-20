from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL") or ""

if not DATABASE_URL:
    DATABASE_URL = "postgresql://username:password@host:port/database"

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS health_data (
    id SERIAL PRIMARY KEY,
    parameter VARCHAR(50),
    value FLOAT,
    unit VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW()
);
""")
conn.commit()

@app.get("/")
def read_root():
    return {"message": "Ваш облачный ИИ-врач жив!"}

@app.post("/add")
def add_data(parameter: str, value: float, unit: str):
    cursor.execute(
        "INSERT INTO health_data (parameter, value, unit) VALUES (%s, %s, %s)",
        (parameter, value, unit)
    )
    conn.commit()
    return {"status": "ok", "parameter": parameter, "value": value}
