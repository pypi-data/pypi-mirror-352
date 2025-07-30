"""
Cross-platform Browser Framework für Web-Automatisierung (Windows & Linux).

Hauptkomponenten:
- BrowserFramework: Kern-Framework für Browser-Steuerung
- ChromiumManager: Download und Setup von Chromium
- BrowserConfig: Konfiguration des Browsers
- Utilities: Hilfsfunktionen und -klassen

Unterstützte Plattformen:
- Windows (x64)
- Linux (x64, ARM64)
"""

from .chromium import ChromiumManager
from .config import (
    AdvancedBrowserConfig,
    BrowserConfig,
    ConfigValidator,
    PlatformConfigFactory,
)
from .core import BrowserFramework
from .exceptions import BrowserError, DownloadError, SetupError
from .types import LocatorStrategy, WebDriverProtocol
from .utils import (
    BrowserHealthChecker,
    CrossPlatformUtils,
    ElementWaiter,
    PerformanceMonitor,
)

# Backward compatibility
BrowserManager = BrowserFramework

__version__ = "1.2.0"
__all__ = [
    # Core Framework
    "BrowserFramework",
    "BrowserManager",  # Backward compatibility

    # Configuration
    "BrowserConfig",
    "AdvancedBrowserConfig",
    "ConfigValidator",
    "PlatformConfigFactory",

    # Chromium Management
    "ChromiumManager",

    # Exceptions
    "BrowserError",
    "SetupError",
    "DownloadError",

    # Utilities
    "ElementWaiter",
    "PerformanceMonitor",
    "BrowserHealthChecker",
    "CrossPlatformUtils",

    # Types
    "LocatorStrategy",
    "WebDriverProtocol",
]
