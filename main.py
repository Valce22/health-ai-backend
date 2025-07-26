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
        # 1. Проверяем, загрузилась ли переменная окружения
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not credentials_json:
            raise HTTPException(status_code=500, detail="GOOGLE_CREDENTIALS_JSON not found in environment variables")
        print("GOOGLE_CREDENTIALS_JSON:", credentials_json[:100])  # первые 100 символов

        # 2. Пробуем декодировать JSON
        try:
            credentials_dict = json.loads(credentials_json)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка декодирования JSON: {str(e)}")

        # 3. Проверяем переменную BUCKET
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            raise HTTPException(status_code=500, detail="GCS_BUCKET_NAME not found in environment variables")
        print("BUCKET_NAME:", bucket_name)

        # 4. Инициализируем клиента и бакет
        client = storage.Client.from_service_account_info(credentials_dict)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file.filename)

        # 5. Читаем содержимое файла
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Пустой файл или ошибка чтения содержимого")
        print(f"Загружается файл: {file.filename}, размер: {len(contents)} байт")

        # 6. Загружаем в Google Cloud
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
