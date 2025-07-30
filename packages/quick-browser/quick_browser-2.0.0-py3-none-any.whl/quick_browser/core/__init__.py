"""
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

from .browser_utilities import BrowserUtilities
from .driver_manager import DriverManager
from .element_interactions import ElementInteractions
from .framework import BrowserFramework
from .profile_manager import ProfileManager
from .troubleshooting import TroubleshootingHelper
from .webdriver_factory import WebDriverFactory

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
