"""Chromium Download und Setup Manager - 64-bit only."""

import logging
import platform
import tempfile
import zipfile
from pathlib import Path

import requests
import win32api

from .config import BrowserConfig
from .download import download_with_progress
from .exceptions import DownloadError, SetupError
from .system import temp_console

logger = logging.getLogger(__name__)


class ChromiumManager:
    """Manager für Chromium-Downloads und -Setup - 64-bit only."""

    PORTABLE_BROWSER_DIR: Path = Path(tempfile.gettempdir()) / "portable_browser"
    CHROMIUM_DIR: Path = PORTABLE_BROWSER_DIR / "chromium"
    ZIP_DIR: Path = PORTABLE_BROWSER_DIR / "zips"
    RELEASES_API: str = (
        "https://api.github.com/repos/"
        "ungoogled-software/ungoogled-chromium-windows/releases/latest"
    )

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialisiert den ChromiumManager.

        Args:
            config: Browser-Konfiguration
        """
        self.config = config
        self._ensure_directories()

        # System-Info loggen falls aktiviert
        if config.log_system_info:
            logger.info(f"System: {platform.platform()}")
            logger.info("Framework: 64-bit only mode")

    def _ensure_directories(self) -> None:
        """Erstellt notwendige Verzeichnisse."""
        self.ZIP_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)

    def get_or_download_chromium(self) -> Path:
        """
        Gibt Pfad zu chrome.exe zurück, lädt bei Bedarf herunter (64-bit only).

        Returns:
            Pfad zu chrome.exe

        Raises:
            SetupError: Bei Setup-Fehlern
        """
        try:
            if self.config.chromium_version:
                zip_path = self._download_specific_chromium()
            else:
                zip_path = self._download_latest_chromium()

            chrome_exe = self._extract_chromium(zip_path)
            logger.info(f"Chromium ready (64-bit): {chrome_exe}")
            return chrome_exe

        except Exception as e:
            raise SetupError(f"Chromium setup failed: {e}") from e

    def _download_latest_chromium(self) -> Path:
        """Lädt neueste Chromium-Version herunter (64-bit only)."""
        logger.info("Fetching latest release info...")

        try:
            response = requests.get(self.RELEASES_API, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise DownloadError(f"Failed to fetch release info: {e}") from e

        # Immer x64 Version suchen
        logger.info("Looking for x64 Chromium release...")

        asset = next(
            (
                a
                for a in data["assets"]
                if "windows_x64" in a["name"].lower() and a["name"].endswith(".zip")
            ),
            None,
        )

        if not asset:
            available_assets = [a["name"] for a in data["assets"]]
            raise DownloadError(
                f"No x64 Chromium asset found.\nAvailable assets: {available_assets}"
            )

        zip_path = self.ZIP_DIR / asset["name"]

        if not zip_path.exists():
            logger.info(f"Downloading {asset['name']}...")

            # Bedingter Console-Aufruf basierend auf show_console Flag
            if self.config.show_console:
                with temp_console("Chromium‑Download"):
                    download_with_progress(
                        asset["browser_download_url"],
                        zip_path,
                        self.config.download_timeout,
                    )
            else:
                # Direkter Download ohne Console
                download_with_progress(
                    asset["browser_download_url"],
                    zip_path,
                    self.config.download_timeout,
                )
        else:
            logger.info("Chromium ZIP already exists")

        return zip_path

    def _download_specific_chromium(self) -> Path:
        """Lädt spezifische Chromium-Version herunter (64-bit only)."""
        if not self.config.chromium_version:
            raise ValueError("Chromium version not specified")

        version = self.config.chromium_version
        tag = f"{version}-1.windows"

        # Immer x64 Dateinamen verwenden
        filename = f"ungoogled-chromium_{version}_windows_x64.zip"

        url = (
            "https://github.com/ungoogled-software/ungoogled-chromium-windows/"
            f"releases/download/{tag}/{filename}"
        )

        zip_path = self.ZIP_DIR / filename

        if not zip_path.exists():
            logger.info(f"Downloading Chromium {version} (x64)...")
            try:
                # Bedingter Console-Aufruf basierend auf show_console Flag
                if self.config.show_console:
                    with temp_console("Chromium‑Download"):
                        download_with_progress(
                            url, zip_path, self.config.download_timeout
                        )
                else:
                    # Direkter Download ohne Console
                    download_with_progress(url, zip_path, self.config.download_timeout)
            except DownloadError as e:
                raise DownloadError(
                    f"Failed to download Chromium {version} (x64): {e}"
                ) from e
        else:
            logger.info("Chromium ZIP already exists")

        return zip_path

    def _extract_chromium(self, zip_path: Path) -> Path:
        """Extrahiert Chromium aus ZIP-Datei."""
        extract_dir = self.CHROMIUM_DIR / zip_path.stem
        chrome_exe = extract_dir / "chrome.exe"

        if chrome_exe.exists():
            logger.info(f"Chromium already extracted: {chrome_exe}")
            return chrome_exe

        logger.info("Extracting Chromium...")
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path) as zip_file:
                zip_file.extractall(self.CHROMIUM_DIR)
        except zipfile.BadZipFile as e:
            raise SetupError(f"Invalid ZIP file: {e}") from e

        if not chrome_exe.exists():
            raise SetupError("chrome.exe not found after extraction")

        return chrome_exe

    @staticmethod
    def get_chrome_version(chrome_exe_path: Path) -> str:
        """
        Ermittelt Chrome-Version aus Datei-Metadaten.

        Args:
            chrome_exe_path: Pfad zu chrome.exe

        Returns:
            Versions-String

        Raises:
            SetupError: Bei Versionserkennung-Fehlern
        """
        try:
            info = win32api.GetFileVersionInfo(str(chrome_exe_path), "\\")
            ms: int = info["FileVersionMS"]
            ls: int = info["FileVersionLS"]
            return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except Exception as e:
            raise SetupError(f"Failed to get Chrome version: {e}") from e

    @staticmethod
    def get_chromedriver_version(chrome_version: str) -> str:
        """
        Ermittelt die passende ChromeDriver-Version für eine Chrome-Version.

        Args:
            chrome_version: Chrome-Version (z.B. "136.0.7103.113")

        Returns:
            ChromeDriver-Version (z.B. "136.0.7103")
        """
        try:
            # Sichere Extraktion der ersten drei Versionsteile
            version_parts = chrome_version.split(".")
            # Wir benötigen nur major.minor.build (die ersten drei Teile)
            if len(version_parts) >= 3:
                return ".".join(version_parts[:3])
            else:
                # Fallback, wenn weniger als 3 Teile vorhanden sind
                return chrome_version
        except Exception as e:
            logger.warning(f"Fehler bei Ermittlung der ChromeDriver-Version: {e}")
            # Im Zweifelsfall die komplette Version zurückgeben
            return chrome_version
