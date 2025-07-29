import os
from datetime import timedelta
from google.cloud.storage import Bucket, Client
from google.oauth2.service_account import Credentials
from pathlib import Path
from typing import Optional, Union
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import SimpleConfig
from .base import GoogleClientManager

class GoogleCloudStorage(GoogleClientManager):
    def __init__(
        self,
        log_config:SimpleConfig,
        service_key:BaseTypes.OptionalString=None,
        credentials:Optional[Credentials]=None,
        credentials_path:Optional[Union[Path, str]]=None,
        bucket_name:BaseTypes.OptionalString = None
    ) -> None:
        key = "google-cloud-storage"
        name = "GoogleCloudStorage"
        super().__init__(key, name, log_config, service_key, credentials, credentials_path)
        self._client = Client(credentials=self._credentials)
        self._bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        if self._bucket_name is None:
            self._client.close()
            raise ValueError("GCS_BUCKET_NAME environment variable must be set if 'bucket_name' is set to None")
        self._bucket = self._client.lookup_bucket(bucket_name=self._bucket_name)
        if self._bucket is None:
            self._client.close()
            raise ValueError(f"Bucket '{self._bucket_name}' does not exist.")
        self._root_location = service_key
        self._logger.info("Client manager initialized successfully")

    @property
    def bucket_name(self) -> str:
        return self._bucket_name

    @property
    def bucket(self) -> Bucket:
        return self._bucket

    def dispose(self) -> None:
        if self._client is not None:
            self._logger.info("Disposing client manager")
            self._client.close()
            self._client = None
            self._logger.info("Client manager disposed successfully")

    def upload(
        self,
        content:bytes,
        location:str,
        content_type:Optional[str]=None,
        make_public:bool=False,
        expiration:timedelta=timedelta(minutes=15),
        root_location_override:BaseTypes.OptionalString=None
    ) -> str:
        """
        Upload a file to Google Cloud Storage.

        Args:
            content (bytes): The file content as bytes.
            location (str): The path inside the bucket to save the file.
            content_type (Optional[str]): MIME type (e.g., 'image/png').
            make_public (bool): Whether to make the file publicly accessible.

        Returns:
            str: The public URL or blob path depending on `make_public`.
        """
        if root_location_override is None or (isinstance(root_location_override, str) and len(root_location_override) <= 0):
            blob = self._bucket.blob(f"{self._root_location}/{location}")
        else:
            blob = self._bucket.blob(f"{root_location_override}/{location}")
        blob.upload_from_string(content, content_type=content_type)

        if make_public:
            blob.make_public()
            url = blob.public_url
        else:
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
        return url

    def generate_signed_url(
        self,
        location:str,
        expiration:timedelta=timedelta(minutes=15),
        root_location_override:BaseTypes.OptionalString=None
    ) -> str:
        """
        generate signed URL of a file in the bucket based on its location.

        Args:
            location: str
                Location of the file inside the bucket

        Returns:
            str: File's pre-signed download url

        Raises:
            ValueError: If the file does not exist
        """
        if root_location_override is None or (isinstance(root_location_override, str) and len(root_location_override) <= 0):
            blob = self._bucket.blob(blob_name=f"{self._root_location}/{location}")
        else:
            blob = self._bucket.blob(blob_name=f"{root_location_override}/{location}")
        if not blob.exists():
            raise ValueError(f"File '{location}' did not exists.")

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        return url