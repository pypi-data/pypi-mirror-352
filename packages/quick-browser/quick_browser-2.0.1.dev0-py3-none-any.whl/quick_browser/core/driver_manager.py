"""ChromeDriver download and management utilities."""

import json
import logging
import shutil
from pathlib import Path
from urllib.request import urlopen

from ..chromium import PlatformDetector, VersionManager
from ..config import BrowserConfig
from ..download import download_with_progress
from ..exceptions import DownloadError, SetupError
from ..system import is_linux, temp_console

logger = logging.getLogger(__name__)


class DriverManager:
    """Manages ChromeDriver download, setup and version compatibility."""

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize driver manager.

        Args:
            config: Browser configuration
        """
        self.config = config
        self.platform_detector = PlatformDetector()
        self.version_manager = VersionManager()

    def ensure_driver(self, chrome_exe: Path) -> str:
        """
        Ensure ChromeDriver is installed (cross-platform).

        Args:
            chrome_exe: Path to Chrome executable

        Returns:
            Path to ChromeDriver

        Raises:
            SetupError: On driver setup errors
        """
        try:
            # Determine ChromeDriver version
            if (
                    self.config.driver_version
                    and self.config.driver_version.lower() != "latest"
            ):
                driver_version = self.config.driver_version
                logger.info(f"Using specified ChromeDriver version: {driver_version}")
            else:
                chrome_version = self.version_manager.get_chrome_version(chrome_exe)
                driver_version = self._get_compatible_chromedriver_version(chrome_version)
                logger.info(
                    f"Auto-detected ChromeDriver version: {driver_version} for Chrome {chrome_version}"
                )

            # Download ChromeDriver directly
            driver_path = self._download_chromedriver_direct(driver_version)
            logger.info(f"ChromeDriver ready: {driver_path}")
            return driver_path

        except Exception as e:
            raise SetupError(f"ChromeDriver setup failed: {e}") from e

    def _get_compatible_chromedriver_version(self, chrome_version: str) -> str:
        """
        Get compatible ChromeDriver version for Chrome version.

        Args:
            chrome_version: Chrome version (e.g. "120.0.6099.109")

        Returns:
            Compatible ChromeDriver version

        Raises:
            SetupError: If no compatible version found
        """
        try:
            # Extract major version
            major_version = chrome_version.split(".")[0]

            # Load available versions from Chrome for Testing API
            url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())

            # Search for newest version for this major version
            compatible_versions = []
            for version_info in data.get("versions", []):
                version = version_info.get("version", "")
                if version.startswith(f"{major_version}."):
                    # Check if ChromeDriver available for platform
                    downloads = version_info.get("downloads", {})
                    chromedriver_downloads = downloads.get("chromedriver", [])

                    # Platform-specific check
                    platform_check = self.platform_detector.get_chromedriver_platform()

                    for download in chromedriver_downloads:
                        if download.get("platform") == platform_check:
                            compatible_versions.append(version)
                            break

            if not compatible_versions:
                raise SetupError(
                    f"No compatible ChromeDriver found for Chrome {chrome_version}"
                )

            # Take newest compatible version
            latest_version = max(
                compatible_versions, key=lambda v: [int(x) for x in v.split(".")]
            )
            return latest_version

        except Exception as e:
            logger.warning(f"Failed to get compatible ChromeDriver version: {e}")
            # Fallback: use Chrome version as ChromeDriver version
            return chrome_version

    def _download_chromedriver_direct(self, version: str) -> str:
        """
        Download ChromeDriver directly from Chrome for Testing (cross-platform).

        Args:
            version: ChromeDriver version

        Returns:
            Path to chromedriver executable

        Raises:
            SetupError: On download errors
        """
        try:
            # Use consistent portable_browser directory structure
            import tempfile
            from pathlib import Path

            portable_browser_dir = Path(tempfile.gettempdir()) / "portable_browser"
            chromedriver_dir = portable_browser_dir / f"chromedriver-{version}"
            executable_name = self.platform_detector.get_chromedriver_executable_name()
            chromedriver_exe = chromedriver_dir / executable_name

            # Check if already exists
            if chromedriver_exe.exists():
                logger.info(f"ChromeDriver already exists: {chromedriver_exe}")
                return str(chromedriver_exe)

            # Create directory
            chromedriver_dir.mkdir(parents=True, exist_ok=True)

            # Get download URL
            download_url = self._get_chromedriver_download_url(version)

            # Download archive file
            platform_str = self.platform_detector.get_chromedriver_platform()
            archive_name = f"chromedriver-{platform_str}.zip"
            archive_path = chromedriver_dir / archive_name

            logger.info(f"Downloading ChromeDriver {version} for {platform_str}...")

            try:
                if self.config.show_console:
                    with temp_console("ChromeDriver Download"):
                        download_with_progress(
                            download_url, archive_path, self.config.download_timeout
                        )
                else:
                    download_with_progress(
                        download_url, archive_path, self.config.download_timeout
                    )
            except DownloadError as e:
                raise SetupError(f"Failed to download ChromeDriver {version}: {e}") from e

            # Extract archive
            logger.info("Extracting ChromeDriver...")
            self._extract_chromedriver(archive_path, chromedriver_dir, executable_name)

            # Remove archive
            archive_path.unlink()

            logger.info(f"ChromeDriver downloaded successfully: {chromedriver_exe}")
            return str(chromedriver_exe)

        except Exception as e:
            if isinstance(e, (SetupError, DownloadError)):
                raise
            raise SetupError(f"Failed to download ChromeDriver: {e}") from e

    @staticmethod
    def _extract_chromedriver(archive_path: Path, extract_dir: Path, executable_name: str) -> None:
        """Extract ChromeDriver from ZIP archive."""
        import zipfile

        try:
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
        except zipfile.BadZipFile as e:
            raise SetupError(f"Invalid ChromeDriver archive file: {e}") from e

        # Find chromedriver executable in extracted files
        chromedriver_exe = extract_dir / executable_name
        for exe_path in extract_dir.rglob(executable_name):
            # Move chromedriver to main directory if needed
            if exe_path != chromedriver_exe:
                shutil.move(str(exe_path), str(chromedriver_exe))
                # Clean up empty subdirectories
                if exe_path.parent != extract_dir and not any(exe_path.parent.iterdir()):
                    exe_path.parent.rmdir()
            break

        if not chromedriver_exe.exists():
            raise SetupError(f"{executable_name} not found in downloaded archive")

        # Set executable permission on Linux
        if is_linux():
            chromedriver_exe.chmod(0o755)

    def _get_chromedriver_download_url(self, version: str) -> str:
        """
        Get download URL for ChromeDriver from Chrome for Testing (cross-platform).

        Args:
            version: ChromeDriver version

        Returns:
            Download URL for current platform

        Raises:
            SetupError: If URL not found
        """
        try:
            # Load download information for specific version
            url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())

            # Get platform
            platform_str = self.platform_detector.get_chromedriver_platform()

            # Search for desired version
            for version_info in data.get("versions", []):
                if version_info.get("version") == version:
                    downloads = version_info.get("downloads", {})
                    chromedriver_downloads = downloads.get("chromedriver", [])

                    # Search for platform-specific download
                    for download in chromedriver_downloads:
                        if download.get("platform") == platform_str:
                            download_url = download.get("url")
                            if download_url:
                                logger.debug(f"Found ChromeDriver download URL from API: {download_url}")
                                return download_url

            # Fallback: use direct URL structure
            fallback_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{platform_str}/chromedriver-{platform_str}.zip"
            logger.warning(f"Version {version} not found in API, using fallback URL: {fallback_url}")
            return fallback_url

        except Exception as e:
            # Last fallback
            platform_str = self.platform_detector.get_chromedriver_platform()
            fallback_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{platform_str}/chromedriver-{platform_str}.zip"
            logger.warning(f"Failed to get download URL from API: {e}, using fallback: {fallback_url}")
            return fallback_url
