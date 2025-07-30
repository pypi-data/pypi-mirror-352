"""Download utilities for ungoogled-chromium and Chromium from Google-free sources."""

import logging
from pathlib import Path
from typing import Any, Dict, List

import requests  # type: ignore[import-untyped]

from ..config import BrowserConfig
from ..download import download_with_progress
from ..exceptions import DownloadError
from ..system import is_linux, is_windows, temp_console
from .platform import PlatformDetector

logger = logging.getLogger(__name__)


class ChromiumDownloader:
    """Download manager for ungoogled-chromium and Chromium from Google-free sources."""

    # Chromium Snapshots (official open-source Chromium builds)
    CHROMIUM_SNAPSHOTS_API = "https://commondatastorage.googleapis.com/chromium-browser-snapshots"

    # ungoogled-chromium sources (plattform-spezifisch)
    UNGOOGLED_SOURCES = {
        "windows": [
            "https://api.github.com/repos/ungoogled-software/ungoogled-chromium-windows/releases/latest",
        ],
        "linux": [
            "https://api.github.com/repos/ungoogled-software/ungoogled-chromium-binaries/releases/latest",
            "https://api.github.com/repos/Eloston/ungoogled-chromium/releases/latest",
        ]
    }

    # Platform mappings for different sources
    PLATFORM_MAPPINGS = {
        "chromium_snapshots": {
            "linux": "Linux_x64",
            "windows": "Win_x64"
        }
    }

    def __init__(self, config: BrowserConfig, zip_dir: Path) -> None:
        """
        Initialize downloader.

        Args:
            config: Browser configuration
            zip_dir: Directory for downloaded archives
        """
        self.config = config
        self.zip_dir = zip_dir
        self.platform_detector = PlatformDetector()

    def download_latest_chromium(self) -> Path:
        """Download latest ungoogled-chromium or Chromium for current platform."""
        logger.info("Downloading latest Google-free Chromium from multiple sources...")

        # Google-free download methods in order of preference
        download_methods = [
            self._download_from_ungoogled_chromium,    # 1. Priority: Google-free
            self._download_from_chromium_snapshots,    # 2. Fallback: Open-source
        ]

        last_error = None
        for method in download_methods:
            try:
                return method()
            except DownloadError as e:
                logger.warning(f"Download method failed: {e}")
                last_error = e
                continue

        # If all methods failed
        raise DownloadError(
            f"All Google-free Chromium download sources failed. Last error: {last_error}"
        )

    def _download_from_ungoogled_chromium(self) -> Path:
        """Download from ungoogled-chromium sources (primary Google-free option)."""
        logger.info("Trying ungoogled-chromium sources...")

        # Get platform-specific sources
        platform_key = self._get_current_platform_key()
        source_urls = self.UNGOOGLED_SOURCES.get(platform_key, [])
        matching_assets: List[Dict[str, Any]] = []

        if not source_urls:
            raise DownloadError(f"No ungoogled-chromium sources for platform: {platform_key}")

        logger.info(f"Using {len(source_urls)} platform-specific sources for {platform_key}")

        for source_url in source_urls:
            try:
                logger.info(f"Checking ungoogled-chromium source: {source_url}")
                response = requests.get(source_url, timeout=30)
                response.raise_for_status()
                data: Dict[str, Any] = response.json()

                # Get assets
                assets: List[Dict[str, Any]] = data.get("assets", [])
                logger.info(f"Found {len(assets)} assets in release")

                # Platform-specific asset selection
                if is_windows():
                    # Windows: Look for .zip files
                    matching_assets = [
                        a for a in assets
                        if a.get("name", "").endswith(".zip")
                        and "x64" in a.get("name", "").lower()
                    ]
                    if not matching_assets:
                        # Fallback: any .zip
                        matching_assets = [
                            a for a in assets
                            if a.get("name", "").endswith(".zip")
                        ]

                elif is_linux():
                    # Linux: Look for .tar.xz files, prefer x64
                    arch_patterns = ["x64", "amd64", "linux"]
                    matching_assets = []

                    for pattern in arch_patterns:
                        candidates = [
                            a for a in assets
                            if (a.get("name", "").endswith((".tar.xz", ".zip"))
                                and pattern in a.get("name", "").lower())
                        ]
                        if candidates:
                            matching_assets = candidates
                            break

                    # Fallback: any .tar.xz or .zip
                    if not matching_assets:
                        matching_assets = [
                            a for a in assets
                            if a.get("name", "").endswith((".tar.xz", ".zip"))
                        ]

                if matching_assets:
                    # Take the first (usually best) match
                    asset = matching_assets[0]
                    logger.info(f"Selected asset: {asset['name']}")

                    zip_path = self.zip_dir / asset["name"]

                    if not zip_path.exists():
                        logger.info(f"Downloading ungoogled-chromium: {asset['name']}...")
                        self._download_with_console(
                            asset["browser_download_url"],
                            zip_path,
                            "Ungoogled Chromium Download"
                        )
                    else:
                        logger.info("Ungoogled Chromium archive already exists")

                    return zip_path
                else:
                    logger.warning(f"No suitable assets found in {source_url}")

            except requests.RequestException as e:
                logger.warning(f"Ungoogled Chromium source failed {source_url}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with {source_url}: {e}")
                continue

        raise DownloadError("All ungoogled-chromium sources failed")

    def _download_from_chromium_snapshots(self) -> Path:
        """Download from Chromium snapshots (open-source fallback)."""
        logger.info("Trying Chromium snapshots...")

        platform_key = self._get_current_platform_key()
        chromium_platform = self.PLATFORM_MAPPINGS["chromium_snapshots"].get(platform_key)

        if not chromium_platform:
            raise DownloadError(f"Unsupported platform for Chromium snapshots: {platform_key}")

        # Get latest snapshot number
        latest_url = f"{self.CHROMIUM_SNAPSHOTS_API}/{chromium_platform}/LAST_CHANGE"
        logger.info(f"Getting latest snapshot from: {latest_url}")

        try:
            response = requests.get(latest_url, timeout=30)
            response.raise_for_status()
            snapshot_number = response.text.strip()
            logger.info(f"Latest snapshot number: {snapshot_number}")
        except requests.RequestException as e:
            raise DownloadError(f"Failed to get latest Chromium snapshot: {e}") from e

        # Construct download URL
        if is_windows():
            filename = "chrome-win.zip"
        else:
            filename = "chrome-linux.zip"

        download_url = f"{self.CHROMIUM_SNAPSHOTS_API}/{chromium_platform}/{snapshot_number}/{filename}"
        zip_path = self.zip_dir / f"chromium-snapshot-{snapshot_number}-{chromium_platform}.zip"

        logger.info(f"Download URL: {download_url}")

        if not zip_path.exists():
            logger.info(f"Downloading Chromium snapshot {snapshot_number}...")
            self._download_with_console(download_url, zip_path, "Chromium Snapshot Download")
        else:
            logger.info("Chromium snapshot already exists")

        return zip_path

    def download_specific_chromium(self, version: str) -> Path:
        """Download specific ungoogled-chromium version for current platform."""
        logger.info(f"Attempting to download ungoogled-chromium version {version}...")

        try:
            return self._download_specific_ungoogled_chromium(version)
        except DownloadError as e:
            logger.warning(f"Ungoogled Chromium failed for version {version}: {e}")
            raise DownloadError(f"Could not download ungoogled-chromium version {version}")

    def _download_specific_ungoogled_chromium(self, version: str) -> Path:
        """Download specific ungoogled-chromium version."""
        logger.info(f"Downloading specific ungoogled-chromium version: {version}")

        # platform_key = self._get_current_platform_key()

        # Construct version-specific URL based on platform
        if is_windows():
            # Windows-specific repository
            base_repo = "ungoogled-software/ungoogled-chromium-windows"
            tag = f"{version}-1"
            # Common Windows filename patterns
            filenames = [
                f"ungoogled-chromium_{version}_windows_x64.zip",
                f"ungoogled-chromium-{version}-windows-x64.zip",
                f"ungoogled-chromium_{version}_x64.zip"
            ]
        else:  # Linux
            # Linux-specific repository
            base_repo = "ungoogled-software/ungoogled-chromium-binaries"
            tag = f"{version}-1"
            # Common Linux filename patterns
            filenames = [
                f"ungoogled-chromium_{version}_linux_x64.tar.xz",
                f"ungoogled-chromium-{version}-linux-x64.tar.xz",
                f"ungoogled-chromium_{version}_x64.tar.xz"
            ]

        logger.info(f"Trying repository: {base_repo}")
        logger.info(f"Looking for tag: {tag}")

        # Try different filename patterns
        for filename in filenames:
            url = f"https://github.com/{base_repo}/releases/download/{tag}/{filename}"
            zip_path = self.zip_dir / filename

            logger.info(f"Trying URL: {url}")

            if not zip_path.exists():
                try:
                    logger.info(f"Downloading ungoogled-chromium {version}: {filename}")
                    self._download_with_console(url, zip_path, "Ungoogled Chromium Download")
                    return zip_path
                except DownloadError as e:
                    logger.warning(f"Download failed for {filename}: {e}")
                    continue
            else:
                logger.info(f"Found existing file: {filename}")
                return zip_path

        raise DownloadError(f"Could not download ungoogled-chromium {version} with any filename pattern")

    @staticmethod
    def _get_current_platform_key() -> str:
        """Get current platform key for mappings."""
        if is_windows():
            return "windows"
        elif is_linux():
            return "linux"
        else:
            raise DownloadError("Unsupported platform")

    def _download_with_console(self, url: str, dest_path: Path, title: str) -> None:
        """Download with optional console display."""
        if self.config.show_console:
            with temp_console(title):
                download_with_progress(url, dest_path, self.config.download_timeout)
        else:
            download_with_progress(url, dest_path, self.config.download_timeout)
