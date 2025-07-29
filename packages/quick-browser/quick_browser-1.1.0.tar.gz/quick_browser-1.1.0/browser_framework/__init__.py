"""
Wiederverwendbares Browser Framework für Web-Automatisierung - 64-bit only.

Hauptkomponenten:
- BrowserFramework: Kern-Framework für Browser-Steuerung
- ChromiumManager: Download und Setup von Chromium
- BrowserConfig: Konfiguration des Browsers
- Utilities: Hilfsfunktionen und -klassen
"""

from .chromium import ChromiumManager
from .config import AdvancedBrowserConfig, BrowserConfig
from .core import BrowserFramework
from .exceptions import BrowserError, DownloadError, SetupError
from .types import LocatorStrategy, WebDriverProtocol
from .utils import BrowserHealthChecker, ElementWaiter, PerformanceMonitor

__version__ = "1.1.0"
__all__ = [
    "BrowserFramework",
    "BrowserConfig",
    "AdvancedBrowserConfig",
    "ChromiumManager",
    "BrowserError",
    "SetupError",
    "DownloadError",
    "ElementWaiter",
    "PerformanceMonitor",
    "BrowserHealthChecker",
    "LocatorStrategy",
    "WebDriverProtocol",
]
