"""Main BrowserFramework orchestrator class."""

import logging
from pathlib import Path
from typing import Any, Optional

from selenium import webdriver

from ..chromium import ChromiumManager
from ..config import BrowserConfig
from ..exceptions import SetupError
from ..utils import CookieBannerConfig, CookieBannerHandler
from .browser_utilities import BrowserUtilities
from .driver_manager import DriverManager
from .element_interactions import ElementInteractions
from .profile_manager import ProfileManager
from .troubleshooting import TroubleshootingHelper
from .webdriver_factory import WebDriverFactory

logger = logging.getLogger(__name__)


class BrowserFramework:
    """
    Cross-platform core framework for browser automation.
    Supports Windows and Linux with automatic cookie banner handling.
    """

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize the BrowserFramework.

        Args:
            config: Browser configuration
        """
        self.config = config

        # Initialize managers
        self.chromium_manager = ChromiumManager(config)
        self.profile_manager = ProfileManager(config.profile_cleanup)
        self.driver_manager = DriverManager(config)
        self.webdriver_factory = WebDriverFactory(config)

        # Runtime state
        self.profile_dir = self.profile_manager.create_random_profile_dir()
        self.chrome_exe: Optional[Path] = None
        self.driver_path: Optional[str] = None
        self.driver: Optional[webdriver.Chrome] = None

        # Utility classes (initialized after driver creation)
        self.element_interactions: Optional[ElementInteractions] = None
        self.browser_utilities: Optional[BrowserUtilities] = None
        self.cookie_handler: Optional[CookieBannerHandler] = None

    def __enter__(self) -> "BrowserFramework":
        """Context Manager Entry."""
        self.setup()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context Manager Exit."""
        self.quit()

    def setup(self) -> None:
        """
        Set up browser through download and initialization.

        Raises:
            SetupError: On setup errors
        """
        try:
            # Get Chromium
            self.chrome_exe = self.chromium_manager.get_or_download_chromium()

            # Get ChromeDriver
            self.driver_path = self.driver_manager.ensure_driver(self.chrome_exe)

            # Create WebDriver
            self.driver = self.webdriver_factory.create_driver(
                self.chrome_exe, self.driver_path, self.profile_dir
            )

            # Initialize utility classes
            self.element_interactions = ElementInteractions(self.driver, self.config.element_timeout)
            self.browser_utilities = BrowserUtilities(self.driver)

            # Initialize cookie banner handler
            self._initialize_cookie_handler()

            platform_name = TroubleshootingHelper.get_platform_name()
            logger.info(f"Browser setup completed successfully ({platform_name})")

        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            TroubleshootingHelper.log_troubleshooting_info(self.chrome_exe, self.driver_path)
            raise SetupError(f"Browser setup failed: {e}") from e

    def _initialize_cookie_handler(self) -> None:
        """Initialize cookie banner handler based on configuration."""
        if not self.driver:
            return

        # Create cookie banner configuration
        cookie_config = CookieBannerConfig(
            prefer_reject=self.config.prefer_reject_cookies,
            timeout_seconds=getattr(self.config, 'cookie_banner_timeout', 5),
            custom_selectors=getattr(self.config, 'custom_cookie_selectors', []),
            verbose=self.config.log_system_info,
        )

        self.cookie_handler = CookieBannerHandler(self.driver, cookie_config)

        if self.config.log_system_info:
            logger.info(f"Cookie banner handler initialized (prefer_reject={self.config.prefer_reject_cookies})")

    def navigate(self, url: str, handle_cookies: Optional[bool] = None) -> bool:
        """
        Navigate to URL with optional automatic cookie banner handling.

        Args:
            url: URL to navigate to
            handle_cookies: Override auto_handle_cookies setting

        Returns:
            True if navigation successful
        """
        if not self.driver:
            raise SetupError("Framework not initialized - call setup() first")

        try:
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")

            # Handle cookies if configured
            should_handle = handle_cookies if handle_cookies is not None else self.config.auto_handle_cookies
            if should_handle and self.cookie_handler:
                self.handle_cookie_banner()

            return True

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    def handle_cookie_banner(self, prefer_reject: Optional[bool] = None) -> bool:
        """
        Handle cookie banners on current page.

        Args:
            prefer_reject: Override prefer_reject_cookies setting

        Returns:
            True if banner was handled
        """
        if not self.cookie_handler:
            logger.warning("Cookie handler not initialized")
            return False

        # Use provided preference or default from config

        if prefer_reject is not None:
            if prefer_reject:
                return self.cookie_handler.handle_banner_reject_all()
            else:
                return self.cookie_handler.handle_banner_accept_all()
        else:
            return self.cookie_handler.handle_banner()

    def get_cookie_statistics(self) -> dict:
        """
        Get cookie banner handling statistics.

        Returns:
            Dictionary with statistics
        """
        if not self.cookie_handler:
            return {"error": "Cookie handler not initialized"}

        return self.cookie_handler.get_statistics()

    def quit(self) -> None:
        """Quit WebDriver and clean up."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")

        # Clean up profile
        self.profile_manager.cleanup_profile(self.profile_dir)

    # Convenience methods for backward compatibility
    def safe_click(self, by: str, value: str, timeout: int = 5) -> bool:
        """Safe click with timeout handling."""
        if not self.element_interactions:
            raise SetupError("Framework not initialized - call setup() first")
        return self.element_interactions.safe_click(by, value, timeout)

    def click_by_id(self, element_id: str, timeout: Optional[int] = None) -> Any:
        """Click element by ID."""
        if not self.element_interactions:
            raise SetupError("Framework not initialized - call setup() first")
        return self.element_interactions.click_by_id(element_id, timeout)

    def click_by_css(self, selector: str, timeout: Optional[int] = None) -> Any:
        """Click element by CSS selector."""
        if not self.element_interactions:
            raise SetupError("Framework not initialized - call setup() first")
        return self.element_interactions.click_by_css(selector, timeout)

    def send_keys_by_name(self, name: str, keys: str, timeout: Optional[int] = None) -> Any:
        """Send keys to element by name."""
        if not self.element_interactions:
            raise SetupError("Framework not initialized - call setup() first")
        return self.element_interactions.send_keys_by_name(name, keys, timeout)

    def remove_elements_by_ids(self, element_ids: tuple) -> None:
        """Remove multiple elements by ID."""
        if not self.browser_utilities:
            raise SetupError("Framework not initialized - call setup() first")
        self.browser_utilities.remove_elements_by_ids(element_ids)

    def scroll_to_element(self, selector: str, behavior: str = "smooth") -> None:
        """Scroll to an element."""
        if not self.browser_utilities:
            raise SetupError("Framework not initialized - call setup() first")
        self.browser_utilities.scroll_to_element(selector, behavior)
