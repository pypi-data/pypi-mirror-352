"""Konfigurationsklassen für das Browser Framework - 64-bit only."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BrowserConfig:
    """Basis-Konfiguration für den Browser - 64-bit only."""

    _credential_target: str = None
    # Browser-Versionen
    chromium_version: Optional[str] = None
    driver_version: Optional[str] = None

    # Browser-Modi
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

    # Vereinfachtes Debugging
    log_system_info: bool = False

    # Performance-Flags
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
        ]
    )

    # Browser-Präferenzen
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
        }
    )


@dataclass(frozen=True)
class AdvancedBrowserConfig(BrowserConfig):
    """Erweiterte Browser-Konfiguration mit zusätzlichen Optionen."""

    # Retry-Konfiguration
    max_retries: int = 3
    retry_delay: float = 1.0

    # Logging-Konfiguration
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Erweiterte Browser-Optionen
    user_agent: Optional[str] = None
    window_size: Optional[Tuple[int, int]] = None
    disable_images: bool = False
    disable_css: bool = False

    def apply_to_driver(self, driver: webdriver.Chrome) -> None:
        """
        Wendet erweiterte Konfiguration auf WebDriver an.

        Args:
            driver: WebDriver-Instanz
        """
        driver.set_page_load_timeout(self.page_load_timeout)
        driver.set_script_timeout(self.script_timeout)
        driver.implicitly_wait(self.implicit_wait)

        if self.window_size:
            driver.set_window_size(*self.window_size)


class ConfigValidator:
    """Validator für Konfigurationen."""

    @staticmethod
    def validate_browser_config(config: BrowserConfig) -> List[str]:
        """
        Validiert Browser-Konfiguration.

        Args:
            config: Zu validierende Konfiguration

        Returns:
            Liste von Validierungsfehlern
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
