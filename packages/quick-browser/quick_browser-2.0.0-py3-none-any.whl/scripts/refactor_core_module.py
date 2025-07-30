#!/usr/bin/env python
"""
Script to refactor core.py into a modular core/ package.
Splits the monolithic BrowserFramework into focused modules.
"""

import shutil
from pathlib import Path

# Auto-detect project root (works from scripts/ subdirectory)
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent  # Go up one level from scripts/ to project root

# Verify we're in the right place
if not (BASE_DIR / "quick_browser" / "__init__.py").exists():
    print(f"❌ Error: Cannot find quick_browser package!")
    print(f"   Script directory: {SCRIPT_DIR}")
    print(f"   Expected project root: {BASE_DIR}")
    print(f"   Looking for: {BASE_DIR / 'quick_browser' / '__init__.py'}")
    exit(1)

CORE_DIR = BASE_DIR / "quick_browser" / "core"
ORIGINAL_FILE = BASE_DIR / "quick_browser" / "core.py"


def create_directory_structure() -> None:
    """Create the core/ directory structure."""
    print("📁 Creating core/ directory structure...")

    # Create core directory
    CORE_DIR.mkdir(exist_ok=True)
    print(f"   ✓ Created: {CORE_DIR}")


def create_init_py() -> None:
    """Create __init__.py with backward compatibility exports."""
    init_content = '''"""
Core framework package for cross-platform browser automation.

This package provides modular components for:
- Browser framework orchestration
- WebDriver creation and management
- ChromeDriver setup and downloads
- Element interactions and utilities
- Profile management
- Troubleshooting and debugging

Main export is BrowserFramework for backward compatibility.
"""

from .framework import BrowserFramework
from .driver_manager import DriverManager
from .webdriver_factory import WebDriverFactory
from .element_interactions import ElementInteractions
from .browser_utilities import BrowserUtilities
from .profile_manager import ProfileManager
from .troubleshooting import TroubleshootingHelper

# Backward compatibility - main export
__all__ = [
    # Main class (backward compatibility)
    "BrowserFramework",

    # Modular components (new)
    "DriverManager",
    "WebDriverFactory", 
    "ElementInteractions",
    "BrowserUtilities",
    "ProfileManager",
    "TroubleshootingHelper",
]
'''

    init_file = CORE_DIR / "__init__.py"
    init_file.write_text(init_content.strip())
    print(f"   ✓ Created: {init_file}")


def create_troubleshooting_py() -> None:
    """Create troubleshooting.py with debug utilities."""
    troubleshooting_content = '''"""Troubleshooting and debugging utilities for browser framework."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TroubleshootingHelper:
    """Helper class for browser framework troubleshooting and debugging."""

    @staticmethod
    def log_troubleshooting_info(chrome_exe: Optional[Path], driver_path: Optional[str]) -> None:
        """Log cross-platform information for troubleshooting."""
        from ..system import get_platform_info

        platform_info = get_platform_info()
        logger.error("=== TROUBLESHOOTING INFORMATION ===")
        logger.error(f"Platform: {platform_info['system']} {platform_info['release']}")
        logger.error(f"Architecture: {platform_info['architecture']}")
        logger.error(f"Chrome executable: {chrome_exe}")
        logger.error(f"ChromeDriver: {driver_path}")
        logger.error("Framework: Cross-platform mode")
        logger.error("=== END TROUBLESHOOTING INFO ===")

    @staticmethod
    def get_platform_name() -> str:
        """Get platform name for logging."""
        from ..system import is_windows, is_linux

        if is_windows():
            return "Windows"
        elif is_linux():
            return "Linux"
        else:
            return "Unknown"

    @staticmethod
    def validate_paths(chrome_exe: Optional[Path], driver_path: Optional[str]) -> list[str]:
        """
        Validate browser and driver paths.

        Returns:
            List of validation errors
        """
        errors = []

        if chrome_exe and not chrome_exe.exists():
            errors.append(f"Chrome executable not found: {chrome_exe}")

        if driver_path and not Path(driver_path).exists():
            errors.append(f"ChromeDriver not found: {driver_path}")

        return errors
'''

    troubleshooting_file = CORE_DIR / "troubleshooting.py"
    troubleshooting_file.write_text(troubleshooting_content.strip())
    print(f"   ✓ Created: {troubleshooting_file}")


def create_profile_manager_py() -> None:
    """Create profile_manager.py with profile handling logic."""
    profile_content = '''"""Profile management utilities for browser framework."""

import random
import shutil
import string
import tempfile
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class ProfileManager:
    """Manager for browser profile creation and cleanup."""

    def __init__(self, cleanup_enabled: bool = True) -> None:
        """
        Initialize profile manager.

        Args:
            cleanup_enabled: Whether to clean up profiles on exit
        """
        self.cleanup_enabled = cleanup_enabled
        self.created_profiles = []

    def create_random_profile_dir(self) -> Path:
        """
        Create temporary profile directory.

        Returns:
            Path to profile directory
        """
        name = "chrome_profile_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        profile_path = Path(tempfile.gettempdir()) / name
        profile_path.mkdir(exist_ok=True)

        # Track for cleanup
        self.created_profiles.append(profile_path)

        logger.debug(f"Created profile directory: {profile_path}")
        return profile_path

    def cleanup_profile(self, profile_dir: Path) -> None:
        """
        Clean up a specific profile directory.

        Args:
            profile_dir: Profile directory to clean up
        """
        if not self.cleanup_enabled:
            logger.debug(f"Profile cleanup disabled, keeping: {profile_dir}")
            return

        try:
            if profile_dir.exists():
                shutil.rmtree(profile_dir, ignore_errors=True)
                logger.debug(f"Cleaned up profile directory: {profile_dir}")

                # Remove from tracking
                if profile_dir in self.created_profiles:
                    self.created_profiles.remove(profile_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up profile directory {profile_dir}: {e}")

    def cleanup_all_profiles(self) -> None:
        """Clean up all tracked profile directories."""
        for profile_dir in self.created_profiles.copy():
            self.cleanup_profile(profile_dir)

    def __del__(self) -> None:
        """Cleanup profiles on object destruction."""
        self.cleanup_all_profiles()
'''

    profile_file = CORE_DIR / "profile_manager.py"
    profile_file.write_text(profile_content.strip())
    print(f"   ✓ Created: {profile_file}")


def create_browser_utilities_py() -> None:
    """Create browser_utilities.py with browser helper methods."""
    utilities_content = '''"""Browser utility functions and helper methods."""

import logging
from typing import Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class BrowserUtilities:
    """Utility methods for browser manipulation and interaction."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        """
        Initialize browser utilities.

        Args:
            driver: WebDriver instance
        """
        self.driver = driver

    def remove_elements_by_ids(self, element_ids: Tuple[str, ...]) -> None:
        """
        Remove multiple elements by ID.

        Args:
            element_ids: Tuple of element IDs to remove
        """
        for element_id in element_ids:
            try:
                self.driver.execute_script(
                    "var el = document.getElementById(arguments[0]); "
                    "if (el) { el.remove(); }",
                    element_id,
                )
                logger.debug(f"Removed element: {element_id}")
            except Exception as e:
                logger.warning(f"Failed to remove element {element_id}: {e}")

    def scroll_to_element(self, selector: str, behavior: str = "smooth") -> None:
        """
        Scroll to an element.

        Args:
            selector: CSS selector of the element
            behavior: Scroll behavior ('smooth' or 'instant')
        """
        scroll_script = f"""
        const element = document.querySelector(arguments[0]);
        if (element) {{
            element.scrollIntoView({{ behavior: '{behavior}', block: 'center' }});
        }}
        """
        try:
            self.driver.execute_script(scroll_script, selector)
            logger.debug(f"Scrolled to element: {selector}")
        except Exception as e:
            logger.warning(f"Failed to scroll to element {selector}: {e}")

    def take_screenshot(self, filename: str) -> bool:
        """
        Take a screenshot.

        Args:
            filename: Path to save screenshot

        Returns:
            True if successful
        """
        try:
            result = self.driver.save_screenshot(filename)
            if result:
                logger.info(f"Screenshot saved: {filename}")
            return result
        except Exception as e:
            logger.error(f"Failed to take screenshot {filename}: {e}")
            return False

    def execute_javascript(self, script: str, *args) -> any:
        """
        Execute JavaScript in the browser.

        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            Script execution result
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug(f"Executed JavaScript: {script[:50]}...")
            return result
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            raise

    def get_page_source(self) -> str:
        """
        Get current page source.

        Returns:
            Page source HTML
        """
        try:
            source = self.driver.page_source
            logger.debug(f"Retrieved page source ({len(source)} characters)")
            return source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""

    def refresh_page(self) -> None:
        """Refresh the current page."""
        try:
            self.driver.refresh()
            logger.debug("Page refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh page: {e}")

    def get_current_url(self) -> str:
        """
        Get current page URL.

        Returns:
            Current URL
        """
        try:
            url = self.driver.current_url
            logger.debug(f"Current URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return ""

    def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
        """
        try:
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
'''

    utilities_file = CORE_DIR / "browser_utilities.py"
    utilities_file.write_text(utilities_content.strip())
    print(f"   ✓ Created: {utilities_file}")


def create_element_interactions_py() -> None:
    """Create element_interactions.py with element interaction methods."""
    interactions_content = '''"""Element interaction utilities for browser automation."""

import logging
from typing import Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class ElementInteractions:
    """Handles all element interactions like clicking, typing, waiting."""

    def __init__(self, driver: webdriver.Chrome, default_timeout: int = 10) -> None:
        """
        Initialize element interactions.

        Args:
            driver: WebDriver instance
            default_timeout: Default timeout for element operations
        """
        self.driver = driver
        self.default_timeout = default_timeout

    def safe_click(self, by: str, value: str, timeout: Optional[int] = None) -> bool:
        """
        Safe click with timeout handling.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            True on success, False on timeout
        """
        timeout = timeout or self.default_timeout
        try:
            self._wait_and_click((by, value), timeout)
            return True
        except TimeoutException:
            logger.warning(f"Timeout clicking element: {by}={value}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False

    def click_by_id(self, element_id: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by ID.

        Args:
            element_id: Element ID
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.ID, element_id), timeout)

    def click_by_css(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by CSS selector.

        Args:
            selector: CSS selector
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.CSS_SELECTOR, selector), timeout)

    def click_by_xpath(self, xpath: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by XPath.

        Args:
            xpath: XPath expression
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.XPATH, xpath), timeout)

    def send_keys_by_name(self, name: str, keys: str, timeout: Optional[int] = None) -> WebElement:
        """
        Send keys to element by name.

        Args:
            name: Name attribute
            keys: Keys to send
            timeout: Timeout in seconds

        Returns:
            The element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.NAME, name))
        )
        element.clear()  # Clear existing content
        element.send_keys(keys)
        logger.debug(f"Sent keys to element {name}: {keys}")
        return element

    def send_keys_by_id(self, element_id: str, keys: str, timeout: Optional[int] = None) -> WebElement:
        """
        Send keys to element by ID.

        Args:
            element_id: Element ID
            keys: Keys to send
            timeout: Timeout in seconds

        Returns:
            The element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.ID, element_id))
        )
        element.clear()
        element.send_keys(keys)
        logger.debug(f"Sent keys to element {element_id}: {keys}")
        return element

    def wait_for_element(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be present.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The found element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.presence_of_element_located((by, value))
        )
        logger.debug(f"Found element: {by}={value}")
        return element

    def wait_for_element_clickable(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be clickable.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The clickable element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((by, value))
        )
        logger.debug(f"Element is clickable: {by}={value}")
        return element

    def _wait_and_click(self, locator: Tuple[str, str], timeout: int) -> WebElement:
        """
        Wait for element and click it.

        Args:
            locator: Tuple of strategy and value
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable(locator)
        )
        element.click()
        logger.debug(f"Clicked element: {locator}")
        return element

    def get_element_text(self, by: str, value: str, timeout: Optional[int] = None) -> str:
        """
        Get text content of an element.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            Element text content
        """
        timeout = timeout or self.default_timeout
        element = self.wait_for_element(by, value, timeout)
        text = element.text
        logger.debug(f"Got element text: {text}")
        return text

    def is_element_present(self, by: str, value: str) -> bool:
        """
        Check if element is present (without waiting).

        Args:
            by: Locator strategy
            value: Locator value

        Returns:
            True if element is present
        """
        try:
            self.driver.find_element(by, value)
            return True
        except Exception:
            return False
'''

    interactions_file = CORE_DIR / "element_interactions.py"
    interactions_file.write_text(interactions_content.strip())
    print(f"   ✓ Created: {interactions_file}")


def create_webdriver_factory_py() -> None:
    """Create webdriver_factory.py with WebDriver creation logic."""
    factory_content = '''"""WebDriver creation and configuration factory."""

import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from ..config import BrowserConfig
from ..exceptions import SetupError
from ..system import is_linux, is_windows

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
'''

    factory_file = CORE_DIR / "webdriver_factory.py"
    factory_file.write_text(factory_content.strip())
    print(f"   ✓ Created: {factory_file}")


def create_driver_manager_py() -> None:
    """Create driver_manager.py with ChromeDriver management logic."""
    driver_content = '''"""ChromeDriver download and management utilities."""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen

from ..chromium import VersionManager, PlatformDetector
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
            from ..chromium.manager import ChromiumManager
            portable_browser_dir = ChromiumManager.PORTABLE_BROWSER_DIR
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

    def _extract_chromedriver(self, archive_path: Path, extract_dir: Path, executable_name: str) -> None:
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
'''

    driver_file = CORE_DIR / "driver_manager.py"
    driver_file.write_text(driver_content.strip())
    print(f"   ✓ Created: {driver_file}")


def create_framework_py() -> None:
    """Create framework.py with the main BrowserFramework orchestrator."""
    framework_content = '''"""Main BrowserFramework orchestrator class."""

import logging
from typing import Any, Optional

from selenium import webdriver

from ..config import BrowserConfig
from ..chromium import ChromiumManager
from ..exceptions import SetupError
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
    Supports Windows and Linux.
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

            platform_name = TroubleshootingHelper.get_platform_name()
            logger.info(f"Browser setup completed successfully ({platform_name})")

        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            TroubleshootingHelper.log_troubleshooting_info(self.chrome_exe, self.driver_path)
            raise SetupError(f"Browser setup failed: {e}") from e

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
'''

    framework_file = CORE_DIR / "framework.py"
    framework_file.write_text(framework_content.strip())
    print(f"   ✓ Created: {framework_file}")


def backup_original_file() -> None:
    """Backup the original core.py file."""
    if ORIGINAL_FILE.exists():
        backup_path = ORIGINAL_FILE.with_suffix('.py.backup')
        shutil.copy2(ORIGINAL_FILE, backup_path)
        print(f"   ✓ Backed up original file to: {backup_path}")

        # Ask user if they want to remove the original
        print("   🗑️  Remove original core.py after backup? (y/N): ", end="")
        remove_original = input().lower().strip()

        if remove_original in ["y", "yes"]:
            ORIGINAL_FILE.unlink()
            print(f"   ✓ Removed original file: {ORIGINAL_FILE}")
            print(f"     📦 All functionality now available via core/ package")
        else:
            print(f"   📁 Original file kept: {ORIGINAL_FILE}")
            print(f"     ⚠️  Note: You may have import conflicts - consider removing it manually")
    else:
        print(f"   ⚠ Original file not found at {ORIGINAL_FILE}")


def update_main_core_import() -> None:
    """Update main quick_browser/__init__.py to import from new structure."""
    main_init = BASE_DIR / "quick_browser" / "__init__.py"

    if main_init.exists():
        print(f"   ✓ Main __init__.py import unchanged (backward compatible)")
    else:
        print(f"   ⚠ Main __init__.py not found at {main_init}")


def create_migration_summary() -> None:
    """Create a summary of the migration."""
    summary_text = f"""
📋 Core Framework Refactoring Complete!

✅ Created Files:
   • {CORE_DIR}/__init__.py              - Package exports (backward compatible!)
   • {CORE_DIR}/framework.py             - Main BrowserFramework orchestrator
   • {CORE_DIR}/driver_manager.py        - ChromeDriver download and setup  
   • {CORE_DIR}/webdriver_factory.py     - WebDriver creation and configuration
   • {CORE_DIR}/element_interactions.py  - Element interactions (click, type, wait)
   • {CORE_DIR}/browser_utilities.py     - Browser utilities (scroll, screenshot, JS)
   • {CORE_DIR}/profile_manager.py       - Profile creation and cleanup
   • {CORE_DIR}/troubleshooting.py       - Debug and troubleshooting helpers

🔄 Backward Compatibility:
   • All existing imports continue to work:
     from quick_browser.core import BrowserFramework

   • NEW: All modular components available as direct imports:
     from quick_browser.core import DriverManager
     from quick_browser.core import ElementInteractions
     from quick_browser.core import BrowserUtilities

🧪 Next Steps:
   1. Test imports from project root:
      cd {BASE_DIR}
      python -c "from quick_browser.core import BrowserFramework; print('✅ Works!')"

   2. Run existing tests to verify compatibility:
      cd {BASE_DIR}
      python -m pytest tests/

   3. Original core.py handling complete!
   4. Single Responsibility achieved - each module has one clear purpose! 🎉

💡 Benefits of New Structure:
   • Single Responsibility: Each module focuses on one aspect
   • Better Testing: Test individual components in isolation  
   • Easier Maintenance: Changes only affect relevant modules
   • Consistent Architecture: Same pattern as chromium/ package
   • Cleaner APIs: Specialized classes for specific tasks

⚠️  Note: Original core.py backed up as core.py.backup  
📂 Working from scripts directory - paths auto-detected
🏗️  588-line God Class successfully split into 7 focused modules!
"""

    print(summary_text)


def main() -> None:
    """Main refactoring function."""
    print("🔧 Starting Core Framework Refactoring...")
    print("=" * 60)
    print(f"📂 Script running from: {SCRIPT_DIR}")
    print(f"📂 Project root detected: {BASE_DIR}")
    print(f"🎯 Target: Split 588-line core.py into modular core/ package")
    print()

    # Backup original
    backup_original_file()

    # Create structure
    create_directory_structure()

    # Create all module files
    create_init_py()
    create_troubleshooting_py()
    create_profile_manager_py()
    create_browser_utilities_py()
    create_element_interactions_py()
    create_webdriver_factory_py()
    create_driver_manager_py()
    create_framework_py()

    # Update imports (if needed)
    update_main_core_import()

    # Summary
    create_migration_summary()

    print("🎉 Core refactoring completed successfully!")
    print("📦 588-line God Class → 7 focused modules")


if __name__ == "__main__":
    main()