"""
Chromium package for cross-platform Chromium and ChromeDriver management.

This package provides modular components for:
- Chromium download and setup
- ChromeDriver version management
- Platform-specific handling
- Archive extraction

All components are available as direct imports for convenience.
"""

from .downloader import ChromiumDownloader
from .extractor import ArchiveExtractor
from .manager import ChromiumManager
from .platform import PlatformDetector
from .version import VersionManager


# Legacy static method exports for backward compatibility
# These were originally static methods on ChromiumManager
def get_chrome_version(chrome_exe_path):
    """Legacy function - use VersionManager.get_chrome_version() instead."""
    return VersionManager.get_chrome_version(chrome_exe_path)


def get_chromedriver_version(chrome_version):
    """Legacy function - use VersionManager.get_chromedriver_version() instead."""
    return VersionManager.get_chromedriver_version(chrome_version)


# Main export for backward compatibility
__all__ = [
    # Primary class (existed in original chromium.py)
    "ChromiumManager",

    # New modular classes (now available as direct imports)
    "PlatformDetector",
    "VersionManager",
    "ChromiumDownloader",
    "ArchiveExtractor",

    # Legacy static functions (for full backward compatibility)
    "get_chrome_version",
    "get_chromedriver_version",
]
