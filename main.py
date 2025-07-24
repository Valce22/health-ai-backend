import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Загружаем JSON из переменной окружения
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not credentials_json:
            raise HTTPException(status_code=500, detail="GOOGLE_CREDENTIALS_JSON not found in environment variables")

        # Декодируем JSON
        credentials_dict = json.loads(credentials_json)

        # Инициализируем клиента Google Cloud Storage
        client = storage.Client.from_service_account_info(credentials_dict)
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            raise HTTPException(status_code=500, detail="GCS_BUCKET_NAME not found in environment variables")

        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file.filename)

        # Загружаем содержимое файла
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)

        return {"filename": file.filename, "message": "File uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data")
def read_data():
    return {"message": "Here is your data endpoint."}

@app.post("/add")
def add_data(parameter: str, value: float, unit: str):
    return {
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "message": "Data added successfully."
    }
