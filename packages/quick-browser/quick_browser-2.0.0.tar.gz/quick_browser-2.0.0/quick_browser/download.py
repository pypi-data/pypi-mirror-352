"""Download utilities for browser assets."""

import logging
import time
from pathlib import Path

import requests

from .exceptions import DownloadError
from .system import safe_tqdm

logger = logging.getLogger(__name__)


def download_with_progress(url: str, dest: Path, timeout: int = 60) -> None:
    """
    Download file with progress bar.

    Args:
        url: Download URL
        dest: Destination path
        timeout: Timeout in seconds

    Raises:
        DownloadError: On download errors
    """
    try:
        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            total = int(response.headers.get("content-length", 0))

            with safe_tqdm(
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
                desc=dest.name,
            ) as progress_bar:
                with open(dest, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            progress_bar.update(len(chunk))

            if total and progress_bar.n != total:
                raise DownloadError("Download incomplete or corrupted")

    except requests.RequestException as e:
        raise DownloadError(f"Download failed: {e}") from e


def wait_for_download_complete(
    download_dir: Path, timeout: int = 60, poll_interval: float = 0.5
) -> None:
    """
    Wait for no more *.crdownload files to exist in download folder.

    Args:
        download_dir: Path to download directory
        timeout: Maximum wait time in seconds
        poll_interval: Polling interval in seconds

    Raises:
        TimeoutError: If *.crdownload files still exist after timeout
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        crdownload_files = list(download_dir.glob("*.crdownload"))
        if not crdownload_files:
            return
        time.sleep(poll_interval)
    raise TimeoutError(
        "Download not completed within timeout period ('.crdownload' files remain)."
    )
