"""
Utils package for cross-platform browser automation utilities.

This package provides modular utility components for:
- Element waiting and interaction utilities
- Browser performance monitoring
- Browser health checking and diagnostics
- Cross-platform utility functions
- Cookie banner handling (NEW!)
- Custom utility helpers

All utilities are available as direct imports for convenience.
"""

from .cookie_banner_handler import CookieBannerConfig, CookieBannerHandler
from .cross_platform import CrossPlatformUtils
from .element_waiter import ElementWaiter
from .health_checker import BrowserHealthChecker
from .performance_monitor import PerformanceMonitor

# from . import CookieBannerHandler, CookieBannerConfig

# Backward compatibility - main exports
__all__ = [
    # Element utilities
    "ElementWaiter",

    # Performance utilities
    "PerformanceMonitor",

    # Health and diagnostics
    "BrowserHealthChecker",

    # Cross-platform utilities
    "CrossPlatformUtils",

    # Cookie banner handling (NEW!)
    "CookieBannerHandler",
    "CookieBannerConfig",
]
