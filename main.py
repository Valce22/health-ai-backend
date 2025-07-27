import os
import json
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import storage

app = FastAPI()

@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to the FastAPI app."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    # Читаем и декодируем credentials из переменной GCS_CREDENTIALS_BASE64
    encoded_credentials = os.getenv("GCS_CREDENTIALS_BASE64")
    if not encoded_credentials:
        raise HTTPException(
            status_code=500,
            detail="GCS_CREDENTIALS_BASE64 environment variable not set",
        )
    try:
        credentials_json = base64.b64decode(encoded_credentials).decode("utf-8")
        credentials_dict = json.loads(credentials_json)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode GCS_CREDENTIALS_BASE64: {exc}",
        )

    # Берём имя бакета
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    if not bucket_name:
        raise HTTPException(
            status_code=500,
            detail="GCS_BUCKET_NAME environment variable not set",
        )

    # Создаём клиента и бакет
    try:
        client = storage.Client.from_service_account_info(credentials_dict)
        bucket = client.bucket(bucket_name)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize GCS client: {exc}",
        )

    # Читаем файл
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file or read error")

    # Загружаем в GCS
    try:
        blob = bucket.blob(file.filename)
        blob.upload_from_string(contents, content_type=file.content_type)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to GCS: {exc}",
        )

    return {"filename": file.filename, "message": "File uploaded successfully."}

@app.get("/data")
def read_data() -> dict:
    return {"message": "Here is your data endpoint."}

@app.post("/add")
def add_data(parameter: str, value: float, unit: str) -> dict:
    return {
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "message": "Data added successfully.",
    }
