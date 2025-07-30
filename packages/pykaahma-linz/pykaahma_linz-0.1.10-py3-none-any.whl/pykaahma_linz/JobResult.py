"""
JobResult.py
"""

import logging
import os
import time
import asyncio
import httpx
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """
    Contains metadata about a completed file download from a Koordinates export job.

    This class is returned by the JobResult.download and JobResult.download_async methods,
    providing detailed information about the downloaded file and its context.

    Attributes:
        folder (str): The directory where the file was saved.
        filename (str): The name of the downloaded file (without path).
        file_path (str): The full path to the downloaded file.
        file_size_bytes (int): The size of the downloaded file in bytes.
        download_url (str): The original download URL provided by the job.
        final_url (str): The final resolved URL after redirects (e.g., S3 location).
        job_id (int): The unique identifier of the export job.
        completed_at (float): The timestamp (seconds since epoch) when the download completed.
        checksum (str | None): The SHA256 checksum of the downloaded file, or None if unavailable.
    """

    folder: str
    filename: str
    file_path: str
    file_size_bytes: int
    download_url: str
    final_url: str
    job_id: int
    completed_at: float
    checksum: str | None = None


class JobResult:
    """
    Represents the result of an asynchronous export or processing job.

    Provides methods to poll for job completion, retrieve job status, and download results.
    The download and download_async methods return a DownloadResult object containing
    detailed metadata about the downloaded file. Download metadata is also stored as
    attributes on the JobResult instance after a successful download.

    Attributes:
        _initial_payload (dict): The initial job payload from the API.
        _job_url (str): The URL to poll for job status.
        _id (int): The unique identifier of the job.
        _poll_interval (int): Polling interval in seconds.
        _timeout (int): Maximum time to wait for job completion in seconds.
        _last_response (dict): The most recent job status response.
        _kserver (KServer): The KServer instance associated with this job.

        # Populated after download:
        download_folder (str): The directory where the file was saved.
        download_filename (str): The name of the downloaded file.
        download_file_path (str): The full path to the downloaded file.
        download_file_size_bytes (int): The size of the downloaded file in bytes.
        download_completed_at (float): The timestamp when the download completed.
        download_resolved_url (str): The final resolved URL after redirects.
        download_checksum (str | None): The SHA256 checksum of the downloaded file.
    """

    def __init__(
        self,
        payload: dict,
        kserver: "KServer",
        poll_interval: int = 10,
        timeout: int = 300,
    ) -> None:
        """
        Initializes the JobResult instance.

        Parameters:
            payload (dict): The job payload, typically from an API response.
            kserver (KServer): The KServer instance associated with this job.
            poll_interval (int, optional): The interval in seconds to poll the job status. Default is 10 seconds.
            timeout (int, optional): The maximum time in seconds to wait for the job to complete. Default is 300 seconds.

        Returns:
            None
        """
        self._initial_payload = payload
        self._job_url = payload["url"]
        self._id = payload["id"]
        self._poll_interval = poll_interval
        self._timeout = timeout
        self._last_response = payload
        self._kserver = kserver

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        """Returns the name of the job."""
        return self._last_response.get("name", "unknown_name")

    @property
    def download_url(self) -> str | None:
        return self._last_response.get("download_url")

    @property
    def status(self) -> str:
        self._refresh_sync()
        return self._last_response.get("state")

    @property
    def progress(self) -> float | None:
        """Returns the progress of the job as a percentage."""
        return self._last_response.get("progress", None)

    @property
    def created_at(self) -> str | None:
        """Returns the creation time of the job."""
        return self._last_response.get("created_at", None)

    def to_dict(self) -> dict:
        return self._last_response

    def __str__(self) -> str:
        self._refresh_sync()
        return (
            f"JobResult(id={self.id}, name='{self.name}', "
            f"status='{self._last_response.get('state')}', "
            f"progress={self.progress})"
        )

    def _refresh_sync(self) -> None:
        """Refresh job status using synchronous HTTP via KServer."""
        self._last_response = self._kserver.get(self._job_url)

    async def _refresh_async(self) -> None:
        """Refresh job status using asynchronous HTTP via KServer."""
        self._last_response = await self._kserver.async_get(self._job_url)

    def output(self) -> dict:
        """
        Blocking: Waits for the job to complete synchronously.

        Returns:
            dict: The final job response after completion.

        Raises:
            TimeoutError: If the job does not complete within the timeout.
            RuntimeError: If the job fails or is cancelled.
        """
        start = time.time()
        # timeout the while loop if it takes more than twenty minutes
        # to complete
        max_time = 1200  # 20 minutes in seconds

        while True and time.time() - start < max_time:
            self._refresh_sync()
            state = self._last_response.get("state")
            if state in ("complete", "failed", "cancelled"):
                break

            if (time.time() - start) > self._timeout:
                raise TimeoutError(
                    f"Export job {self._id} did not complete within timeout."
                )

            time.sleep(self._poll_interval)

        if self._last_response.get("state") != "complete":
            raise RuntimeError(
                f"Export job {self._id} failed with state: {self._last_response.get('state')}"
            )

        return self._last_response

    async def output_async(self) -> dict:
        """
        Non-blocking: Waits for the job to complete asynchronously.

        Returns:
            dict: The final job response after completion.

        Raises:
            TimeoutError: If the job does not complete within the timeout.
            RuntimeError: If the job fails or is cancelled.
        """
        start = asyncio.get_event_loop().time()
        max_time = 600  # 10 minutes in seconds
        while True and (asyncio.get_event_loop().time() - start < max_time):
            await self._refresh_async()
            state = self._last_response.get("state")
            logger.debug(f"Job {self._id} state: {state} progress: {self.progress}")
            if state in ("complete", "failed", "cancelled"):
                break

            if (asyncio.get_event_loop().time() - start) > self._timeout:
                raise TimeoutError(
                    f"Export job {self._id} did not complete within timeout."
                )

            await asyncio.sleep(self._poll_interval)

        if self._last_response.get("state") != "complete":
            raise RuntimeError(
                f"Export job {self._id} failed with state: {self._last_response.get('state')}"
            )

        return self._last_response

    def download(self, folder: str, file_name: str | None = None) -> DownloadResult:
        """
        Waits for job to finish, then downloads the file synchronously.

        Parameters:
            folder (str): The folder where the file will be saved.
            file_name (str, optional): The name of the file to save. If None, uses job name.

        Returns:
            DownloadResult: An object containing details about the downloaded file.

        Raises:
            ValueError: If the download URL is not available.
        """

        self.output()  # ensure job is complete
        if not self.download_url:
            raise ValueError(
                "Download URL not available. Job may not have completed successfully."
            )

        file_name = f"{file_name}.zip" if file_name else f"{self.name}.zip"
        file_path = os.path.join(folder, file_name)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        headers = {"Authorization": f"key {self._kserver._api_key}"}

        with httpx.Client(follow_redirects=True) as client:
            resp = client.get(self.download_url, headers=headers, follow_redirects=True)
            resp.raise_for_status()
            final_url = str(resp.url)

            with client.stream("GET", final_url) as r, open(file_path, "wb") as f:
                r.raise_for_status()
                for chunk in r.iter_bytes():
                    f.write(chunk)

        file_size_bytes = os.path.getsize(file_path)
        checksum = None
        try:
            with open(file_path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
        except Exception:
            pass
        completed_at = time.time()

        # Set as attributes on the JobResult instance
        self.download_folder = folder
        self.download_filename = file_name
        self.download_file_path = file_path
        self.download_file_size_bytes = file_size_bytes
        self.download_completed_at = completed_at
        self.download_resolved_url = final_url
        self.download_checksum = checksum

        return DownloadResult(
            folder=folder,
            filename=file_name,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            download_url=self.download_url,
            final_url=final_url,
            job_id=self._id,
            completed_at=completed_at,
            checksum=checksum,
        )
