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
    )
    bucket = client.bucket("health-ai-valce-file")  # заменишь на имя своего бакета!
    contents = await file.read()
    blob = bucket.blob(file.filename)
    blob.upload_from_string(contents)
    return {"status": "ok", "filename": file.filename}
