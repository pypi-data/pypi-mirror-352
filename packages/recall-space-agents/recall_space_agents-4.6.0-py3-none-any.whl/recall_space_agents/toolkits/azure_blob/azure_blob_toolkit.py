import asyncio
import pickle
from typing import List
from datetime import datetime, timedelta

# Azure Blob Storage (asynchronous) library
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, ContentSettings

# If you have a similar ToolBuilder from your agent framework:
# from agent_builder.builders.tool_builder import ToolBuilder
# For demonstration purposes, if the above import is not available,
# you may need to comment it out or provide your own ToolBuilder mechanism.
from agent_builder.builders.tool_builder import ToolBuilder

# Import the schema mappings from the other file (updated to remove container_name)
from recall_space_agents.toolkits.azure_blob.schema_mappings import schema_mappings


class AzureBlobToolkit:
    """
    Azure Blob Toolkit
    ==================

    This toolkit provides asynchronous methods for interacting with Azure Blob
    Storage using a connection string. It supports listing files/folders in a
    specified path, reading file bytes, and reading Python pickled objects
    stored in blobs.

    Container Name Assumption:
    --------------------------
    A single container_name is specified at initialization, removing the need
    to pass the container_name for each operation. All operations interact
    with the configured container.

    Setup Instructions for Azure Blob Storage Integration:
    ------------------------------------------------------
    1. Create an Azure Storage account or use an existing one.
    2. Go to the Azure Portal > Storage accounts, and locate your storage account.
    3. Obtain the connection string from the "Access keys" section.
    4. Use this connection string in the AzureBlobToolkit constructor.
    5. Ensure that the container you're targeting exists, or create one.
    6. Use the asynchronous methods below to interact with your blobs.
    """

    def __init__(self, connection_string: str, container_name: str):
        """
        Initialize the toolkit with a connection string and container name.

        Args:
            connection_string (str): Azure Storage account connection string.
            container_name (str): Name of the Azure container to use for all operations.
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_name = container_name
        self.schema_mappings = schema_mappings

    async def alist_files_in_folder(self, folder_path: str) -> List[str]:
        """
        List files and possibly subfolders under a given folder path in the configured container.
        """
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        # Azure does not have a true folder hierarchy; we can filter by 'name_starts_with'.
        blob_list = container_client.list_blobs(name_starts_with=folder_path)
        results = []
        async for blob in blob_list:
            results.append(blob.name)
        return results

    async def aread_file(self, blob_name: str) -> bytes:
        """
        Read the contents of a blob as raw bytes from the configured container.
        """
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        blob_client = container_client.get_blob_client(blob_name)
        downloader = await blob_client.download_blob()
        data = await downloader.readall()
        return data

    async def aread_pickle(self, blob_name: str):
        """
        Read a blob as pickled Python data from the configured container.
        """
        data_bytes = await self.aread_file(blob_name)
        return pickle.loads(data_bytes)

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit, based
        on the schema_mappings. Each tool can be integrated into your agent framework.
        """
        tools = []
        for method_name, method_info in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=method_name)
            tool_builder.set_function(getattr(self, method_name))
            tool_builder.set_coroutine(getattr(self, method_name))
            tool_builder.set_description(description=method_info["description"])
            tool_builder.set_schema(schema=method_info["input_schema"])
            tool = tool_builder.build()
            tools.append(tool)
        return tools

    async def aupload_file(
        self,
        blob_name: str,
        file_bytes: bytes,
        content_type: str = None,
        expiry_minutes: int = 60,
    ) -> str:
        """
        Upload a file and return a secure time-limited SAS download URL.

        Args:
            blob_name (str): Target blob name (optionally with folder path).
            file_bytes (bytes): File contents.
            content_type (str, optional): MIME type (e.g., "application/pdf")
            expiry_minutes (int): Minutes until the SAS link expires.

        Returns:
            str: Downloadable SAS URL for the blob.
        """
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        blob_client = container_client.get_blob_client(blob_name)
        if content_type:
            content_settings = ContentSettings(content_type=content_type)
            await blob_client.upload_blob(
                file_bytes, overwrite=True, content_settings=content_settings
            )
        else:
            await blob_client.upload_blob(file_bytes, overwrite=True)
        sas_url = self.get_blob_sas_url(blob_name, expiry_minutes=expiry_minutes)
        return sas_url

    def get_blob_sas_url(self, blob_name: str, expiry_minutes: int = 60) -> str:
        """
        Generate a SAS-signed URL for this blob. The URL allows public download access
        for the duration specified by expiry_minutes.
        """
        account_name = self.blob_service_client.account_name

        # Azure's async SDK stores the credential differently:
        # Get key either from .credential.account_key or .credential._account_key
        account_key = None
        cred = getattr(self.blob_service_client, "credential", None)
        if hasattr(cred, "account_key"):
            account_key = cred.account_key
        elif hasattr(cred, "_account_key"):
            account_key = cred._account_key
        if account_key is None:
            raise RuntimeError("Could not extract account key for SAS token creation.")

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=expiry_minutes),
        )

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        return f"{blob_client.url}?{sas_token}"
