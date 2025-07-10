from fastapi import FastAPI, File, UploadFile
import psycopg2
from google.cloud import storage
import json
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
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    client = storage.Client.from_service_account_info(
        json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON"))
    
    bucket = client.bucket("health-ai-valce-file")  # Замени на имя своего ведра!
    contents = await file.read()
    blob = bucket.blob(file.filename)
    blob.upload_from_string(contents)
    return {"status": "ok", "filename": file.filename}


@app.get("/data")
def read_data():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, parameter, value, unit, timestamp FROM health_data ORDER BY timestamp DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [
        {
            "id": row[0],
            "parameter": row[1],
            "value": row[2],
            "unit": row[3],
            "timestamp": row[4].isoformat()
        }
        for row in rows
    ]
    return {"data": data}    #Trigger redeploy: add comment
