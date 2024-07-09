from logging import getLogger

from azure.storage.blob import BlobServiceClient

logger = getLogger(__name__)


class BlobClient:
    def __init__(
        self,
        account_name: str,
        container_name: str,
        sas_token: str,
    ):
        self.account_name = account_name
        self.container_name = container_name
        self.sas_token = sas_token

    def get_blob_service_client(self) -> BlobServiceClient:
        return BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential=self.sas_token,
        )

    def download_blob_stream(
        self,
        blob_name: str,
    ) -> bytes:
        blob_service_client = self.get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name,
        )
        stream = blob_client.download_blob().readall()
        logger.info(f"Downloaded blob {blob_name} from container {self.container_name}")
        return stream

    def upload_blob_stream(
        self,
        blob_name: str,
        stream: bytes,
    ):
        blob_service_client = self.get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name,
        )
        blob_client.upload_blob(stream, overwrite=True)
        logger.info(f"Uploaded blob {blob_name} to container {self.container_name}")

    def list_blobs(
        self,
    ) -> list:
        blob_service_client = self.get_blob_service_client()
        container_client = blob_service_client.get_container_client(self.container_name)
        logger.info(f"Listed blobs in container {self.container_name}")
        return [blob.name for blob in container_client.list_blobs()]
