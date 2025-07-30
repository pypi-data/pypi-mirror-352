"""
Cross-platform Browser Framework for Web Automation (Windows & Linux).

Main Components:
- BrowserFramework: Core framework for browser control
- ChromiumManager: Download and setup of Chromium
- BrowserConfig: Browser configuration
- Utilities: Helper functions and classes

Supported Platforms:
- Windows (x64)
- Linux (x64, ARM64)
"""

from ._version import __version__
from .chromium import ChromiumManager
from .cli import test_framework
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
    CookieBannerConfig,
    CookieBannerHandler,
    CrossPlatformUtils,
    ElementWaiter,
    PerformanceMonitor,
)

# Backward compatibility
BrowserManager = BrowserFramework

__all__ = [
    # Version
    "__version__",

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

    # CLI
    "test_framework",
]
