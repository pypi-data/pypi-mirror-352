"""Cross-platform configuration classes for the Browser Framework."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BrowserConfig:
    """Cross-platform base configuration for the browser."""

    _credential_target: str = None
    # Browser versions
    chromium_version: Optional[str] = None
    driver_version: Optional[str] = None

    # Browser modes
    headless: bool = False
    kiosk: bool = True
    show_console: bool = False

    # Timeouts
    download_timeout: int = 60
    element_timeout: int = 20
    page_load_timeout: int = 30
    script_timeout: int = 30
    implicit_wait: int = 5

    # Cleanup
    profile_cleanup: bool = True

    # Cross-platform debugging
    log_system_info: bool = False

    # Cookie banner handling (NEW!)
    auto_handle_cookies: bool = False  # Automatically handle cookie banners
    prefer_reject_cookies: bool = True  # Prefer rejecting cookies over accepting

    # Cross-platform performance flags
    performance_flags: List[str] = field(
        default_factory=lambda: [
            "--disable-extensions",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-translate",
            "--ignore-certificate-errors",
            "--no-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--dns-prefetch-disable",
            "--disable-session-crashed-bubble",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-sync",
            "--metrics-recording-only",
            "--mute-audio",
            "--autoplay-policy=user-gesture-required",
            "--window-position=0,0",
            # Linux-specific flags (ignored on Windows)
            "--disable-gpu-sandbox",
            "--disable-software-rasterizer",
        ]
    )

    # Cross-platform browser preferences
    browser_prefs: Dict[str, Any] = field(
        default_factory=lambda: {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
            "profile.managed_default_content_settings.stylesheets": 1,
            "profile.managed_default_content_settings.cookies": 1,
            "profile.managed_default_content_settings.javascript": 1,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "download.default_directory": str(Path.home() / "Downloads"),
            "disk-cache-size": 4096,
            # Cross-platform settings
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        }
    )


@dataclass(frozen=True)
class AdvancedBrowserConfig(BrowserConfig):
    """Advanced cross-platform browser configuration with additional options."""

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0

    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Advanced browser options
    user_agent: Optional[str] = None
    window_size: Optional[Tuple[int, int]] = None
    disable_images: bool = False
    disable_css: bool = False

    # Cross-platform specific options
    use_xvfb: bool = False  # For Linux headless with GUI tests
    display_number: Optional[int] = None  # X11 Display for Linux

    # Advanced cookie banner options
    cookie_banner_timeout: int = 8  # Timeout for cookie banner detection
    custom_cookie_selectors: List[Tuple[str, str]] = field(default_factory=list)  # Custom banner selectors

    def apply_to_driver(self, driver: webdriver.Chrome) -> None:
        """
        Apply advanced configuration to WebDriver.

        Args:
            driver: WebDriver instance
        """
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.set_script_timeout(self.script_timeout)
        driver.implicitly_wait(self.implicit_wait)

        if self.window_size:
            driver.set_window_size(*self.window_size)

    def get_platform_specific_flags(self) -> List[str]:
        """
        Determine platform-specific Chrome flags.

        Returns:
            List of platform-specific flags
        """
        import sys

        flags = []

        if sys.platform.startswith('linux'):
            # Linux-specific flags
            flags.extend([
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu-sandbox",
                "--disable-software-rasterizer",
            ])

            if self.use_xvfb:
                display = self.display_number or 99
                flags.append(f"--display=:{display}")

        elif sys.platform == 'win32':
            # Windows-specific flags
            flags.extend([
                "--disable-gpu-process-crash-limit",
            ])

        return flags


class ConfigValidator:
    """Cross-platform validator for configurations."""

    @staticmethod
    def validate_browser_config(config: BrowserConfig) -> List[str]:
        """
        Validate browser configuration cross-platform.

        Args:
            config: Configuration to validate

        Returns:
            List of validation errors
        """
        errors = []

        if config.download_timeout <= 0:
            errors.append("download_timeout must be positive")

        if config.element_timeout <= 0:
            errors.append("element_timeout must be positive")

        if config.page_load_timeout <= 0:
            errors.append("page_load_timeout must be positive")

        if config.chromium_version and not config.chromium_version.count(".") >= 2:
            errors.append("chromium_version must be in format X.Y.Z.W")

        return errors

    @staticmethod
    def validate_platform_compatibility(config: BrowserConfig) -> List[str]:
        """
        Validate platform compatibility.

        Args:
            config: Configuration to validate

        Returns:
            List of platform-specific warnings
        """
        import platform
        import sys

        warnings = []

        # Architecture check
        arch = platform.machine().lower()
        if arch not in ['x86_64', 'amd64', 'aarch64', 'arm64']:
            warnings.append(f"Architecture {arch} may not be fully supported")

        # Platform-specific validations
        if sys.platform == 'win32':
            # Windows-specific checks
            if config.show_console and hasattr(config, 'use_xvfb') and config.use_xvfb:
                warnings.append("use_xvfb is not supported on Windows")

        elif sys.platform.startswith('linux'):
            # Linux-specific checks
            if config.kiosk:
                warnings.append("Kiosk mode behavior may differ on Linux")

        return warnings


class PlatformConfigFactory:
    """Factory for platform-optimized configurations."""

    @staticmethod
    def create_windows_config(**kwargs) -> BrowserConfig:
        """
        Create Windows-optimized configuration.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Windows-optimized BrowserConfig
        """
        defaults = {
            'show_console': True,  # Windows can handle console well
            'kiosk': True,  # Windows kiosk works well
        }
        defaults.update(kwargs)
        return BrowserConfig(**defaults)

    @staticmethod
    def create_linux_config(**kwargs) -> BrowserConfig:
        """
        Create Linux-optimized configuration.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Linux-optimized BrowserConfig
        """
        defaults = {
            'show_console': False,  # Linux terminal handling differs
            'kiosk': False,  # Linux fullscreen instead of kiosk
        }
        defaults.update(kwargs)
        return BrowserConfig(**defaults)

    @staticmethod
    def create_auto_config(**kwargs) -> BrowserConfig:
        """
        Create automatically platform-optimized configuration.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Platform-optimized BrowserConfig
        """
        import sys

        if sys.platform == 'win32':
            return PlatformConfigFactory.create_windows_config(**kwargs)
        elif sys.platform.startswith('linux'):
            return PlatformConfigFactory.create_linux_config(**kwargs)
        else:
            # Fallback for other platforms
            return BrowserConfig(**kwargs)

    @staticmethod
    def create_cookie_friendly_config(**kwargs) -> BrowserConfig:
        """
        Create configuration optimized for sites with cookie banners.

        Args:
            **kwargs: Additional configuration parameters

        Returns:
            Cookie-friendly BrowserConfig
        """
        defaults = {
            'auto_handle_cookies': True,
            'prefer_reject_cookies': True,
            'element_timeout': 15,  # Longer timeout for banner detection
            'headless': False,  # Banners often don't work in headless
        }
        defaults.update(kwargs)
        return BrowserConfig(**defaults)
