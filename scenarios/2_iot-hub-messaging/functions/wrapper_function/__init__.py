from os import getenv

import fastapi
from dotenv import load_dotenv
from fastapi import UploadFile

from .blobs import BlobClient

load_dotenv()

app = fastapi.FastAPI()
blob_client = BlobClient(
    account_name=getenv("BLOB_STORAGE_ACCOUNT_NAME", ""),
    container_name=getenv("BLOB_STORAGE_CONTAINER_NAME", ""),
    sas_token=getenv("BLOB_STORAGE_SAS_TOKEN", ""),
)


@app.get("/info")
async def info():
    return {
        "scenario": "iot-hub-messaging",
    }


@app.get(
    "/images/{device_name}/{blob_name}",
    responses={200: {"content": {"image/jpeg": {}}}},
    response_class=fastapi.responses.Response,
)
async def get_image(
    device_name: str,
    blob_name: str,
):
    image_bytes = blob_client.download_blob_stream(
        blob_name=f"{device_name}/{blob_name}",
    )
    return fastapi.responses.Response(
        content=image_bytes,
        media_type="image/jpeg",
    )


@app.get(
    "/images",
)
async def list_images():
    images = blob_client.list_blobs()
    return images


@app.post(
    "/images",
    status_code=201,
)
async def upload_blob(
    file: UploadFile,
    blob_name: str,
):
    content = await file.read()
    blob_client.upload_blob_stream(
        blob_name=blob_name,
        stream=content,
    )
    return {
        "blob_name": blob_name,
    }
