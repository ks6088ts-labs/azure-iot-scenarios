from os import getenv

import fastapi
from dotenv import load_dotenv
from fastapi import UploadFile, status
from fastapi.responses import JSONResponse

from .blobs import BlobClient
from .iothubs import IotHubClient
from .openais import OpenAiClient

load_dotenv()

app = fastapi.FastAPI()
blob_client = BlobClient(
    account_name=getenv("BLOB_STORAGE_ACCOUNT_NAME", ""),
    container_name=getenv("BLOB_STORAGE_CONTAINER_NAME", ""),
    sas_token=getenv("BLOB_STORAGE_SAS_TOKEN", ""),
)
openai_client = OpenAiClient(
    api_key=getenv("OPENAI_API_KEY", ""),
    api_version=getenv("OPENAI_API_VERSION", ""),
    endpoint=getenv("OPENAI_ENDPOINT", ""),
    gpt_model=getenv("OPENAI_GPT_MODEL", ""),
)
iothub_client = IotHubClient(
    device_connection_string=getenv("IOTHUB_DEVICE_CONNECTION_STRING", ""),
    connection_string=getenv("IOTHUB_CONNECTION_STRING", ""),
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


@app.post(
    "/explain_image",
    status_code=201,
)
async def explain_image(
    file: UploadFile,
    system_prompt: str = "You are a helpful assistant.",
    user_prompt: str = "Please explain the attached image.",
):
    image = await file.read()
    response = openai_client.create_chat_completions_with_vision(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        image=image,
    )
    return {
        "response": response,
    }


@app.get(
    "/iothub/device_twin",
    status_code=200,
)
async def get_device_twin():
    device_twin = await iothub_client.get_device_twin()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=device_twin,
    )


@app.post(
    "/iothub/invoke_direct_method",
    status_code=201,
)
async def invoke_direct_method(
    device_id="device001",
    method_name="capture_image",
    payload={"index": "0"},
):
    try:
        response = iothub_client.invoke_direct_method(
            device_id=device_id,
            method_name=method_name,
            payload=payload,
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response,
    )
