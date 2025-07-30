"""WebDriver creation and configuration factory."""

import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from ..config import BrowserConfig
from ..exceptions import SetupError
from ..system import is_linux

logger = logging.getLogger(__name__)


class WebDriverFactory:
    """Factory for creating and configuring WebDriver instances."""

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize WebDriver factory.

        Args:
            config: Browser configuration
        """
        self.config = config

    def create_driver(self, chrome_exe: Path, driver_path: str, profile_dir: Path) -> webdriver.Chrome:
        """
        Create and configure WebDriver (cross-platform).

        Args:
            chrome_exe: Path to Chrome executable
            driver_path: Path to ChromeDriver
            profile_dir: Profile directory path

        Returns:
            Configured Chrome WebDriver instance

        Raises:
            SetupError: On driver creation errors
        """
        try:
            logger.info(f"Creating WebDriver with Chrome: {chrome_exe}")
            logger.info(f"Using ChromeDriver: {driver_path}")

            options = self._create_chrome_options(chrome_exe, profile_dir)
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            # Set timeouts
            self._configure_timeouts(driver)

            logger.info("WebDriver created successfully")
            return driver

        except Exception as e:
            raise SetupError(f"Failed to create WebDriver: {e}") from e

    def _create_chrome_options(self, chrome_exe: Path, profile_dir: Path) -> Options:
        """
        Create Chrome options with configuration.

        Args:
            chrome_exe: Path to Chrome executable
            profile_dir: Profile directory path

        Returns:
            Configured Chrome options
        """
        options = Options()
        options.binary_location = str(chrome_exe)
        options.add_argument(f"--user-data-dir={profile_dir}")

        # Platform-specific window options
        self._add_window_options(options)

        # Performance flags
        self._add_performance_flags(options)

        # Browser preferences
        self._add_browser_preferences(options)

        return options

    def _add_window_options(self, options: Options) -> None:
        """Add window-related options."""
        if self.config.kiosk:
            if is_linux():
                # On Linux handle kiosk mode differently
                options.add_argument("--start-fullscreen")
            else:
                options.add_argument("--kiosk")
        else:
            options.add_argument("--start-maximized")

        if self.config.headless:
            options.add_argument("--headless=new")

    def _add_performance_flags(self, options: Options) -> None:
        """Add performance-related flags."""
        for flag in self.config.performance_flags:
            options.add_argument(flag)

        # Linux-specific flags
        if is_linux():
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # X11-specific flags for better compatibility
            options.add_argument("--disable-gpu-sandbox")

    def _add_browser_preferences(self, options: Options) -> None:
        """Add browser preferences."""
        options.add_experimental_option("prefs", self.config.browser_prefs)
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )

    def _configure_timeouts(self, driver: webdriver.Chrome) -> None:
        """Configure WebDriver timeouts."""
        driver.set_page_load_timeout(self.config.page_load_timeout)
        driver.set_script_timeout(self.config.script_timeout)
        driver.implicitly_wait(self.config.implicit_wait)

        logger.debug(f"Configured timeouts: page_load={self.config.page_load_timeout}, "
                     f"script={self.config.script_timeout}, implicit={self.config.implicit_wait}")
