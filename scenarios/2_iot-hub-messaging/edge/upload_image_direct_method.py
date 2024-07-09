# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import os
import pprint
import time
from logging import getLogger

import cv2
from azure.core.exceptions import ResourceExistsError
from azure.iot.device import MethodResponse
from azure.iot.device.aio import IoTHubDeviceClient
from azure.storage.blob import BlobClient

logger = getLogger(__name__)


async def upload_via_storage_blob(blob_info, image_data: bytes):
    sas_url = "https://{}/{}/{}{}".format(
        blob_info["hostName"],
        blob_info["containerName"],
        blob_info["blobName"],
        blob_info["sasToken"],
    )
    blob_client = BlobClient.from_blob_url(sas_url)
    return blob_client.upload_blob(image_data)


# https://github.com/Azure/azure-iot-sdk-python/blob/main/samples/async-hub-scenarios/upload_to_blob.py
async def upload_to_blob(
    device_client: IoTHubDeviceClient,
    blob_name: str,
    image_data: bytes,
):
    # get the Storage SAS information from IoT Hub.
    storage_info = await device_client.get_storage_info_for_blob(blob_name)
    result = {"status_code": -1, "status_description": "N/A"}

    # Using the Storage Blob V12 API, perform the blob upload.
    try:
        upload_result = await upload_via_storage_blob(storage_info, image_data)
        if hasattr(upload_result, "error_code"):
            result = {
                "status_code": upload_result.error_code,
                "status_description": "Storage Blob Upload Error",
            }
        else:
            result = {"status_code": 200, "status_description": ""}
    except ResourceExistsError as ex:
        if ex.status_code:
            result = {"status_code": ex.status_code, "status_description": ex.reason}
        else:
            print("Failed with Exception: {}", ex)
            result = {"status_code": 400, "status_description": ex.message}

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(result)

    if result["status_code"] == 200:
        await device_client.notify_blob_upload_status(
            storage_info["correlationId"],
            True,
            result["status_code"],
            result["status_description"],
        )
    else:
        await device_client.notify_blob_upload_status(
            storage_info["correlationId"],
            False,
            result["status_code"],
            result["status_description"],
        )


async def capture_image(
    device_client: IoTHubDeviceClient,
    blob_name: str,
    camera_index=0,
) -> tuple[int, dict]:
    print("capturing image...")

    camera = cv2.VideoCapture(
        index=camera_index,
    )  # 0 is the camera index, it can be changed to the camera index of your camera

    # wait seconds to warm up camera: https://hironsan.hatenablog.com/entry/2017/06/08/151239
    time.sleep(2)

    return_value, image = camera.read()
    del camera
    if not return_value:
        return 500, {
            "result": False,
            "data": "Error capturing image",
        }
    image_data = cv2.imencode(".jpg", image)[1].tobytes()

    try:
        await upload_to_blob(
            device_client=device_client,
            blob_name=blob_name,
            image_data=image_data,
        )
    except Exception as ex:
        print("Failed with Exception: {}", ex)
        return 500, {
            "result": False,
            "data": "Error uploading image",
        }
    return 200, {
        "result": True,
        "data": "Image uploaded successfully",
    }


async def main():
    # The connection string for a device should never be stored in code. For the sake of simplicity we're using an environment variable here.
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # The client object is used to interact with your Azure IoT hub.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # connect the client.
    await device_client.connect()

    # Define behavior for handling methods
    async def method_request_handler(method_request):
        # Determine how to respond to the method request based on the method name
        if method_request.name == "capture_image":
            status, payload = await capture_image(
                device_client=device_client,
                blob_name=time.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg",
            )
            print("executed capture_image")
        else:
            status = 400
            payload = {
                "result": False,
                "data": "unknown method",
            }

        # Send the response
        method_response = MethodResponse.create_from_method_request(
            method_request, status, payload
        )
        await device_client.send_method_response(method_response)

    # Set the method request handler on the client
    device_client.on_method_request_received = method_request_handler

    # Define behavior for halting the application
    def stdin_listener():
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)

    # Wait for user to indicate they are done listening for method calls
    await user_finished

    # Finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
