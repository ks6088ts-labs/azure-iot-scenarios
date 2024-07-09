from logging import getLogger

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod, CloudToDeviceMethodResult

logger = getLogger(__name__)


class IotHubClient:
    def __init__(
        self,
        device_connection_string: str,
        connection_string: str,
    ) -> None:
        self.device_connection_string = device_connection_string
        self.connection_string = connection_string

    async def get_device_twin(self) -> dict:
        client = IoTHubDeviceClient.create_from_connection_string(
            self.device_connection_string
        )
        # FIXME: connection should not be closed after each operation
        await client.connect()
        twin = await client.get_twin()
        await client.shutdown()
        return twin

    def invoke_direct_method(
        self,
        method_name: str,
        payload: str,
        device_id: str,
    ) -> dict:
        registry_manager = IoTHubRegistryManager(self.connection_string)
        # Call the direct method.
        deviceMethod = CloudToDeviceMethod(
            method_name=method_name,
            payload=payload,
        )
        response: CloudToDeviceMethodResult = registry_manager.invoke_device_method(
            device_id=device_id,
            direct_method_request=deviceMethod,
        )
        return response.as_dict()
