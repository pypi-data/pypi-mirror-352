"""Main ChromiumManager class that orchestrates Chromium and ChromeDriver management."""

import logging
import tempfile
from pathlib import Path

from ..config import BrowserConfig
from ..exceptions import SetupError
from .downloader import ChromiumDownloader
from .extractor import ArchiveExtractor
from .platform import PlatformDetector
from .version import VersionManager

logger = logging.getLogger(__name__)


class ChromiumManager:
    """Cross-platform manager for Chromium downloads and setup."""

    PORTABLE_BROWSER_DIR: Path = Path(tempfile.gettempdir()) / "portable_browser"
    CHROMIUM_DIR: Path = PORTABLE_BROWSER_DIR / "chromium"
    ZIP_DIR: Path = PORTABLE_BROWSER_DIR / "zips"

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize the ChromiumManager.

        Args:
            config: Browser configuration
        """
        self.config = config
        self.platform_detector = PlatformDetector()
        self.downloader = ChromiumDownloader(config, self.ZIP_DIR)
        self.extractor = ArchiveExtractor()
        self.version_manager = VersionManager()

        self._ensure_directories()

        # Log system info if enabled
        if config.log_system_info:
            from ..system import get_platform_info
            platform_info = get_platform_info()
            logger.info(f"System: {platform_info['system']} {platform_info['release']}")
            logger.info(f"Architecture: {platform_info['architecture']}")
            logger.info("Framework: Cross-platform mode")

    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        self.ZIP_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)

    def get_or_download_chromium(self) -> Path:
        """
        Return path to chrome/chromium, download if needed.

        Returns:
            Path to chrome/chromium executable

        Raises:
            SetupError: On setup errors
        """
        try:
            if self.config.chromium_version:
                zip_path = self.downloader.download_specific_chromium(self.config.chromium_version)
            else:
                zip_path = self.downloader.download_latest_chromium()

            executable_path = self._extract_chromium(zip_path)
            platform_name = self.platform_detector.get_platform_name()
            logger.info(f"Chromium ready ({platform_name}): {executable_path}")
            return executable_path

        except Exception as e:
            raise SetupError(f"Chromium setup failed: {e}") from e

    def _extract_chromium(self, archive_path: Path) -> Path:
        """Extract Chromium from archive file."""
        extract_dir = self.CHROMIUM_DIR / archive_path.stem
        executable_name = self.platform_detector.get_executable_name()

        return self.extractor.extract_chromium(archive_path, extract_dir, executable_name)

    # Legacy methods for backward compatibility
    def get_chrome_version(self, chrome_exe_path: Path) -> str:
        """Get Chrome version (legacy method)."""
        return self.version_manager.get_chrome_version(chrome_exe_path)

    def get_chromedriver_version(self, chrome_version: str) -> str:
        """Get ChromeDriver version (legacy method)."""
        return self.version_manager.get_chromedriver_version(chrome_version)

    # Static methods for backward compatibility
    @staticmethod
    def get_chrome_version_static(chrome_exe_path: Path) -> str:
        """Static method for backward compatibility."""
        return VersionManager.get_chrome_version(chrome_exe_path)

    @staticmethod
    def get_chromedriver_version_static(chrome_version: str) -> str:
        """Static method for backward compatibility."""
        return VersionManager.get_chromedriver_version(chrome_version)
