"""Download-Utilities für Browser-Assets."""

import logging
import time
from pathlib import Path

import requests

from .exceptions import DownloadError
from .system import safe_tqdm

logger = logging.getLogger(__name__)


def download_with_progress(url: str, dest: Path, timeout: int = 60) -> None:
    """
    Lädt Datei mit Fortschrittsanzeige herunter.

    Args:
        url: Download-URL
        dest: Ziel-Pfad
        timeout: Timeout in Sekunden

    Raises:
        DownloadError: Bei Download-Fehlern
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
    Wartet darauf, dass keine *.crdownload-Dateien mehr im Download-Ordner existieren.

    Args:
        download_dir: Pfad zum Download-Verzeichnis
        timeout: Maximale Wartezeit in Sekunden
        poll_interval: Abfrageintervall in Sekunden

    Raises:
        TimeoutError: Wenn nach Timeout noch *.crdownload-Dateien existieren
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        crdownload_files = list(download_dir.glob("*.crdownload"))
        if not crdownload_files:
            return
        time.sleep(poll_interval)
    raise TimeoutError(
        "Download nicht innerhalb der Timeout-Periode abgeschlossen ('.crdownload' bleibt vorhanden)."
    )
