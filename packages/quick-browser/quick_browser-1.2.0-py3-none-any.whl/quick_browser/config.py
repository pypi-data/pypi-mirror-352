"""Cross-platform Konfigurationsklassen für das Browser Framework."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BrowserConfig:
    """Cross-platform Basis-Konfiguration für den Browser."""

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

    # Cross-platform Debugging
    log_system_info: bool = False

    # Cross-platform Performance-Flags
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
            # Linux-spezifische Flags (werden unter Windows ignoriert)
            "--disable-gpu-sandbox",
            "--disable-software-rasterizer",
        ]
    )

    # Cross-platform Browser-Präferenzen
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
            # Cross-platform Einstellungen
            "profile.default_content_setting_values.automatic_downloads": 1,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        }
    )


@dataclass(frozen=True)
class AdvancedBrowserConfig(BrowserConfig):
    """Erweiterte Cross-platform Browser-Konfiguration mit zusätzlichen Optionen."""

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

    # Cross-platform spezifische Optionen
    use_xvfb: bool = False  # Für Linux headless mit GUI-Tests
    display_number: Optional[int] = None  # X11 Display für Linux

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

    def get_platform_specific_flags(self) -> List[str]:
        """
        Ermittelt plattform-spezifische Chrome-Flags.

        Returns:
            Liste von plattform-spezifischen Flags
        """
        import sys

        flags = []

        if sys.platform.startswith('linux'):
            # Linux-spezifische Flags
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
            # Windows-spezifische Flags
            flags.extend([
                "--disable-gpu-process-crash-limit",
            ])

        return flags


class ConfigValidator:
    """Cross-platform Validator für Konfigurationen."""

    @staticmethod
    def validate_browser_config(config: BrowserConfig) -> List[str]:
        """
        Validiert Browser-Konfiguration cross-platform.

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

    @staticmethod
    def validate_platform_compatibility(config: BrowserConfig) -> List[str]:
        """
        Validiert Plattform-Kompatibilität.

        Args:
            config: Zu validierende Konfiguration

        Returns:
            Liste von Plattform-spezifischen Warnungen
        """
        import platform
        import sys

        warnings = []

        # Architektur-Prüfung
        arch = platform.machine().lower()
        if arch not in ['x86_64', 'amd64', 'aarch64', 'arm64']:
            warnings.append(f"Architecture {arch} may not be fully supported")

        # Plattform-spezifische Validierungen
        if sys.platform == 'win32':
            # Windows-spezifische Prüfungen
            if config.show_console and hasattr(config, 'use_xvfb') and config.use_xvfb:
                warnings.append("use_xvfb is not supported on Windows")

        elif sys.platform.startswith('linux'):
            # Linux-spezifische Prüfungen
            if config.kiosk:
                warnings.append("Kiosk mode behavior may differ on Linux")

        return warnings


class PlatformConfigFactory:
    """Factory für plattform-optimierte Konfigurationen."""

    @staticmethod
    def create_windows_config(**kwargs) -> BrowserConfig:
        """
        Erstellt Windows-optimierte Konfiguration.

        Args:
            **kwargs: Zusätzliche Konfigurationsparameter

        Returns:
            Windows-optimierte BrowserConfig
        """
        defaults = {
            'show_console': True,  # Windows kann Console gut handhaben
            'kiosk': True,  # Windows Kiosk funktioniert gut
        }
        defaults.update(kwargs)
        return BrowserConfig(**defaults)

    @staticmethod
    def create_linux_config(**kwargs) -> BrowserConfig:
        """
        Erstellt Linux-optimierte Konfiguration.

        Args:
            **kwargs: Zusätzliche Konfigurationsparameter

        Returns:
            Linux-optimierte BrowserConfig
        """
        defaults = {
            'show_console': False,  # Linux Terminal-Handling anders
            'kiosk': False,  # Linux Fullscreen statt Kiosk
        }
        defaults.update(kwargs)
        return BrowserConfig(**defaults)

    @staticmethod
    def create_auto_config(**kwargs) -> BrowserConfig:
        """
        Erstellt automatisch plattform-optimierte Konfiguration.

        Args:
            **kwargs: Zusätzliche Konfigurationsparameter

        Returns:
            Plattform-optimierte BrowserConfig
        """
        import sys

        if sys.platform == 'win32':
            return PlatformConfigFactory.create_windows_config(**kwargs)
        elif sys.platform.startswith('linux'):
            return PlatformConfigFactory.create_linux_config(**kwargs)
        else:
            # Fallback für andere Plattformen
            return BrowserConfig(**kwargs)
