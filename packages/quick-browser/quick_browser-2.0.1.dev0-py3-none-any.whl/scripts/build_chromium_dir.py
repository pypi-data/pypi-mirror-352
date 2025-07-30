#!/usr/bin/env python
"""
Script to refactor chromium.py into a modular chromium/ package.
Splits the monolithic chromium.py into focused modules.
"""

import os
import shutil
from pathlib import Path
from typing import Dict

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

CHROMIUM_DIR = BASE_DIR / "quick_browser" / "chromium"
ORIGINAL_FILE = BASE_DIR / "quick_browser" / "chromium.py"


def create_directory_structure() -> None:
    """Create the chromium/ directory structure."""
    print("📁 Creating chromium/ directory structure...")

    # Create chromium directory
    CHROMIUM_DIR.mkdir(exist_ok=True)
    print(f"   ✓ Created: {CHROMIUM_DIR}")


def create_init_py() -> None:
    """Create __init__.py with backward compatibility exports."""
    init_content = '''"""
Chromium package for cross-platform Chromium and ChromeDriver management.

This package provides modular components for:
- Chromium download and setup
- ChromeDriver version management  
- Platform-specific handling
- Archive extraction

All components are available as direct imports for convenience.
"""

from .manager import ChromiumManager
from .platform import PlatformDetector  
from .version import VersionManager
from .downloader import ChromiumDownloader
from .extractor import ArchiveExtractor

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
'''

    init_file = CHROMIUM_DIR / "__init__.py"
    init_file.write_text(init_content.strip())
    print(f"   ✓ Created: {init_file}")


def create_platform_py() -> None:
    """Create platform.py with platform detection logic."""
    platform_content = '''"""Platform detection and platform-specific utilities for Chromium management."""

import platform
from typing import Dict, Any

from ..exceptions import SetupError
from ..system import is_linux, is_windows


class PlatformDetector:
    """Platform detection and platform-specific configuration."""

    @staticmethod
    def get_platform_name() -> str:
        """Determine platform name for ungoogled-chromium."""
        if is_windows():
            return "windows"
        elif is_linux():
            return "linux"
        else:
            raise SetupError(f"Unsupported platform: {platform.system()}")

    @staticmethod
    def get_platform_archive_pattern() -> str:
        """Determine archive pattern for current platform."""
        arch = platform.machine().lower()

        if is_windows():
            # Windows supports only x64
            if arch in ["amd64", "x86_64"]:
                return "windows_x64"
            else:
                raise SetupError(f"Unsupported Windows architecture: {arch}")

        elif is_linux():
            # Linux supports x64 and ARM64
            if arch in ["x86_64", "amd64"]:
                return "linux_x64"
            elif arch in ["aarch64", "arm64"]:
                return "linux_arm64"
            else:
                raise SetupError(f"Unsupported Linux architecture: {arch}")

        else:
            raise SetupError(f"Unsupported platform: {platform.system()}")

    @staticmethod
    def get_executable_name() -> str:
        """Determine executable file name."""
        if is_windows():
            return "chrome.exe"
        else:  # Linux
            return "chrome"

    @staticmethod
    def get_chromedriver_platform() -> str:
        """Determine ChromeDriver platform string."""
        if is_windows():
            # Windows supports only win64
            return "win64"
        elif is_linux():
            # Linux supports linux64 and linux-arm64
            arch = platform.machine().lower()
            if arch in ["x86_64", "amd64"]:
                return "linux64"
            elif arch in ["aarch64", "arm64"]:
                return "linux-arm64"
            else:
                raise SetupError(f"Unsupported Linux architecture: {arch}")
        else:
            raise SetupError("Unsupported platform for ChromeDriver")

    @staticmethod
    def get_chromedriver_executable_name() -> str:
        """Determine ChromeDriver executable name."""
        if is_windows():
            return "chromedriver.exe"
        else:  # Linux
            return "chromedriver"

    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """Get comprehensive platform information."""
        return {
            "platform_name": PlatformDetector.get_platform_name(),
            "archive_pattern": PlatformDetector.get_platform_archive_pattern(),
            "executable_name": PlatformDetector.get_executable_name(),
            "chromedriver_platform": PlatformDetector.get_chromedriver_platform(),
            "chromedriver_executable": PlatformDetector.get_chromedriver_executable_name(),
            "is_windows": is_windows(),
            "is_linux": is_linux(),
            "architecture": platform.machine().lower(),
        }
'''

    platform_file = CHROMIUM_DIR / "platform.py"
    platform_file.write_text(platform_content.strip())
    print(f"   ✓ Created: {platform_file}")


def create_version_py() -> None:
    """Create version.py with version management logic."""
    version_content = '''"""Version management and compatibility checking for Chromium and ChromeDriver."""

import json
import logging
import subprocess
from pathlib import Path
from urllib.request import urlopen

from ..exceptions import SetupError
from ..system import is_linux, is_windows

logger = logging.getLogger(__name__)


class VersionManager:
    """Version management for Chromium and ChromeDriver compatibility."""

    @staticmethod
    def get_chrome_version(chrome_exe_path: Path) -> str:
        """
        Determine Chrome version cross-platform.

        Args:
            chrome_exe_path: Path to chrome/chromium executable

        Returns:
            Version string

        Raises:
            SetupError: On version detection errors
        """
        try:
            if is_windows():
                return VersionManager._get_chrome_version_windows(chrome_exe_path)
            else:  # Linux
                return VersionManager._get_chrome_version_linux(chrome_exe_path)
        except Exception as e:
            raise SetupError(f"Failed to get Chrome version: {e}") from e

    @staticmethod
    def _get_chrome_version_windows(chrome_exe_path: Path) -> str:
        """Windows-specific version detection."""
        try:
            import win32api
            # Use chr() to avoid quote conflicts
            backslash_str = chr(92) + chr(92)
            info = win32api.GetFileVersionInfo(str(chrome_exe_path), backslash_str)
            ms: int = info["FileVersionMS"]
            ls: int = info["FileVersionLS"]
            return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except ImportError:
            # Fallback if win32api not available
            return VersionManager._get_chrome_version_subprocess(chrome_exe_path)

    @staticmethod
    def _get_chrome_version_linux(chrome_exe_path: Path) -> str:
        """Linux-specific version detection."""
        return VersionManager._get_chrome_version_subprocess(chrome_exe_path)

    @staticmethod
    def _get_chrome_version_subprocess(chrome_exe_path: Path) -> str:
        """Version detection via subprocess (cross-platform fallback)."""
        try:
            result = subprocess.run(
                [str(chrome_exe_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse version from output like "Chromium 120.0.6099.109"
                version_line = result.stdout.strip()
                parts = version_line.split()
                for part in parts:
                    if part.count(".") >= 2:  # Version format X.Y.Z.W
                        return part

            raise SetupError(f"Could not parse version from: {result.stdout}")

        except subprocess.TimeoutExpired:
            raise SetupError("Chrome version check timed out")
        except subprocess.SubprocessError as e:
            raise SetupError(f"Failed to get Chrome version via subprocess: {e}")

    @staticmethod
    def get_chromedriver_version(chrome_version: str) -> str:
        """
        Determine compatible ChromeDriver version for Chrome version.

        Args:
            chrome_version: Chrome version (e.g. "136.0.7103.113")

        Returns:
            ChromeDriver version (e.g. "136.0.7103")
        """
        try:
            # Safe extraction of first three version parts
            version_parts = chrome_version.split(".")
            # We only need major.minor.build (first three parts)
            if len(version_parts) >= 3:
                return ".".join(version_parts[:3])
            else:
                # Fallback if less than 3 parts available
                return chrome_version
        except Exception as e:
            logger.warning(f"Error determining ChromeDriver version: {e}")
            # In doubt, return complete version
            return chrome_version
'''

    version_file = CHROMIUM_DIR / "version.py"
    version_file.write_text(version_content.strip())
    print(f"   ✓ Created: {version_file}")


def create_extractor_py() -> None:
    """Create extractor.py with archive extraction logic."""
    extractor_content = '''"""Archive extraction utilities for Chromium and ChromeDriver packages."""

import logging
import tarfile
import zipfile
from pathlib import Path

from ..exceptions import SetupError
from ..system import is_linux

logger = logging.getLogger(__name__)


class ArchiveExtractor:
    """Archive extraction utilities for different formats."""

    @staticmethod
    def extract_chromium(archive_path: Path, extract_dir: Path, executable_name: str) -> Path:
        """
        Extract Chromium from archive file.

        Args:
            archive_path: Path to archive file
            extract_dir: Directory to extract to
            executable_name: Name of executable to find

        Returns:
            Path to extracted executable

        Raises:
            SetupError: On extraction errors
        """
        executable_path = extract_dir / executable_name

        if executable_path.exists():
            logger.info(f"Chromium already extracted: {executable_path}")
            return executable_path

        logger.info("Extracting Chromium...")
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            if archive_path.suffix == '.zip':
                ArchiveExtractor._extract_zip(archive_path, extract_dir)
            elif archive_path.suffix == '.xz':
                ArchiveExtractor._extract_tar_xz(archive_path, extract_dir)
            else:
                raise SetupError(f"Unsupported archive format: {archive_path.suffix}")

        except Exception as e:
            raise SetupError(f"Extraction failed: {e}") from e

        # Search for executable file
        for exe_path in extract_dir.rglob(executable_name):
            if exe_path.is_file():
                # Set executable permission on Linux
                if is_linux():
                    exe_path.chmod(0o755)
                return exe_path

        raise SetupError(f"{executable_name} not found after extraction")

    @staticmethod
    def _extract_zip(archive_path: Path, extract_dir: Path) -> None:
        """Extract ZIP file."""
        try:
            with zipfile.ZipFile(archive_path) as zip_file:
                zip_file.extractall(extract_dir)
        except zipfile.BadZipFile as e:
            raise SetupError(f"Invalid ZIP file: {e}") from e

    @staticmethod
    def _extract_tar_xz(archive_path: Path, extract_dir: Path) -> None:
        """Extract TAR.XZ file (Linux)."""
        try:
            with tarfile.open(archive_path, 'r:xz') as tar_file:
                tar_file.extractall(extract_dir)
        except tarfile.TarError as e:
            raise SetupError(f"Invalid TAR.XZ file: {e}") from e
'''

    extractor_file = CHROMIUM_DIR / "extractor.py"
    extractor_file.write_text(extractor_content.strip())
    print(f"   ✓ Created: {extractor_file}")


def create_downloader_py() -> None:
    """Create downloader.py with download logic."""
    downloader_content = '''"""Download utilities for Chromium and ChromeDriver from various sources."""

import json
import logging
from pathlib import Path
from urllib.request import urlopen

import requests

from ..config import BrowserConfig
from ..download import download_with_progress
from ..exceptions import DownloadError, SetupError
from ..system import temp_console, is_windows
from .platform import PlatformDetector

logger = logging.getLogger(__name__)


class ChromiumDownloader:
    """Download manager for Chromium and ChromeDriver."""

    # API for ungoogled-chromium releases
    RELEASES_API: str = (
        "https://api.github.com/repos/"
        "ungoogled-software/ungoogled-chromium-{platform}/releases/latest"
    )

    def __init__(self, config: BrowserConfig, zip_dir: Path) -> None:
        """
        Initialize downloader.

        Args:
            config: Browser configuration
            zip_dir: Directory for downloaded archives
        """
        self.config = config
        self.zip_dir = zip_dir
        self.platform_detector = PlatformDetector()

    def download_latest_chromium(self) -> Path:
        """Download latest Chromium version for current platform."""
        platform_name = self.platform_detector.get_platform_name()
        api_url = self.RELEASES_API.format(platform=platform_name)

        logger.info(f"Fetching latest release info for {platform_name}...")

        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise DownloadError(f"Failed to fetch release info: {e}") from e

        # Search for asset for current platform/architecture
        platform_pattern = self.platform_detector.get_platform_archive_pattern()
        logger.info(f"Looking for {platform_pattern} Chromium release...")

        asset = next(
            (
                a
                for a in data["assets"]
                if platform_pattern in a["name"].lower() and a["name"].endswith((".zip", ".tar.xz"))
            ),
            None,
        )

        if not asset:
            available_assets = [a["name"] for a in data["assets"]]
            raise DownloadError(
                f"No {platform_pattern} Chromium asset found.\\n"
                f"Available assets: {available_assets}"
            )

        zip_path = self.zip_dir / asset["name"]

        if not zip_path.exists():
            asset_name = asset.get("name", "unknown")
            logger.info(f"Downloading {asset_name}...")
            self._download_with_console(asset["browser_download_url"], zip_path, "Chromium Download")
        else:
            logger.info("Chromium archive already exists")

        return zip_path

    def download_specific_chromium(self, version: str) -> Path:
        """Download specific Chromium version for current platform."""
        platform_name = self.platform_detector.get_platform_name()
        platform_pattern = self.platform_detector.get_platform_archive_pattern()

        # Tag format differs for different platforms
        if is_windows():
            tag = f"{version}-1.windows"
            filename = f"ungoogled-chromium_{version}_{platform_pattern}.zip"
        else:  # Linux
            tag = f"{version}-1"
            filename = f"ungoogled-chromium_{version}_{platform_pattern}.tar.xz"

        url = (
            f"https://github.com/ungoogled-software/ungoogled-chromium-{platform_name}/"
            f"releases/download/{tag}/{filename}"
        )

        zip_path = self.zip_dir / filename

        if not zip_path.exists():
            logger.info(f"Downloading Chromium {version} ({platform_pattern})...")
            try:
                self._download_with_console(url, zip_path, "Chromium Download")
            except DownloadError as e:
                raise DownloadError(
                    f"Failed to download Chromium {version} ({platform_pattern}): {e}"
                ) from e
        else:
            logger.info("Chromium archive already exists")

        return zip_path

    def _download_with_console(self, url: str, dest_path: Path, title: str) -> None:
        """Download with optional console display."""
        if self.config.show_console:
            with temp_console(title):
                download_with_progress(url, dest_path, self.config.download_timeout)
        else:
            download_with_progress(url, dest_path, self.config.download_timeout)
'''

    downloader_file = CHROMIUM_DIR / "downloader.py"
    downloader_file.write_text(downloader_content.strip())
    print(f"   ✓ Created: {downloader_file}")


def create_manager_py() -> None:
    """Create manager.py with the main ChromiumManager class."""
    manager_content = '''"""Main ChromiumManager class that orchestrates Chromium and ChromeDriver management."""

import logging
import tempfile
from pathlib import Path

from ..config import BrowserConfig
from ..exceptions import SetupError
from .downloader import ChromiumDownloader
from .extractor import ArchiveExtractor
from .platform import PlatformDetector
from .version import VersionManager

logger = logging.getLogger(__name__)


class ChromiumManager:
    """Cross-platform manager for Chromium downloads and setup."""

    PORTABLE_BROWSER_DIR: Path = Path(tempfile.gettempdir()) / "portable_browser"
    CHROMIUM_DIR: Path = PORTABLE_BROWSER_DIR / "chromium"
    ZIP_DIR: Path = PORTABLE_BROWSER_DIR / "zips"

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialize the ChromiumManager.

        Args:
            config: Browser configuration
        """
        self.config = config
        self.platform_detector = PlatformDetector()
        self.downloader = ChromiumDownloader(config, self.ZIP_DIR)
        self.extractor = ArchiveExtractor()
        self.version_manager = VersionManager()

        self._ensure_directories()

        # Log system info if enabled
        if config.log_system_info:
            from ..system import get_platform_info
            platform_info = get_platform_info()
            logger.info(f"System: {platform_info['system']} {platform_info['release']}")
            logger.info(f"Architecture: {platform_info['architecture']}")
            logger.info("Framework: Cross-platform mode")

    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        self.ZIP_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)

    def get_or_download_chromium(self) -> Path:
        """
        Return path to chrome/chromium, download if needed.

        Returns:
            Path to chrome/chromium executable

        Raises:
            SetupError: On setup errors
        """
        try:
            if self.config.chromium_version:
                zip_path = self.downloader.download_specific_chromium(self.config.chromium_version)
            else:
                zip_path = self.downloader.download_latest_chromium()

            executable_path = self._extract_chromium(zip_path)
            platform_name = self.platform_detector.get_platform_name()
            logger.info(f"Chromium ready ({platform_name}): {executable_path}")
            return executable_path

        except Exception as e:
            raise SetupError(f"Chromium setup failed: {e}") from e

    def _extract_chromium(self, archive_path: Path) -> Path:
        """Extract Chromium from archive file."""
        extract_dir = self.CHROMIUM_DIR / archive_path.stem
        executable_name = self.platform_detector.get_executable_name()

        return self.extractor.extract_chromium(archive_path, extract_dir, executable_name)

    # Legacy methods for backward compatibility
    def get_chrome_version(self, chrome_exe_path: Path) -> str:
        """Get Chrome version (legacy method)."""
        return self.version_manager.get_chrome_version(chrome_exe_path)

    def get_chromedriver_version(self, chrome_version: str) -> str:
        """Get ChromeDriver version (legacy method)."""
        return self.version_manager.get_chromedriver_version(chrome_version)

    # Static methods for backward compatibility
    @staticmethod
    def get_chrome_version_static(chrome_exe_path: Path) -> str:
        """Static method for backward compatibility."""
        return VersionManager.get_chrome_version(chrome_exe_path)

    @staticmethod
    def get_chromedriver_version_static(chrome_version: str) -> str:
        """Static method for backward compatibility."""
        return VersionManager.get_chromedriver_version(chrome_version)
'''

    manager_file = CHROMIUM_DIR / "manager.py"
    manager_file.write_text(manager_content.strip())
    print(f"   ✓ Created: {manager_file}")


def create_usage_examples() -> None:
    """Create usage examples file showing new import patterns."""
    examples_content = """#!/usr/bin/env python
'''
Usage examples for the new modular chromium package.
Demonstrates all available import patterns and backward compatibility.
'''

# ✅ BACKWARD COMPATIBLE - Works exactly like before
from quick_browser.chromium import ChromiumManager

# ✅ NEW - Direct access to modular components  
from quick_browser.chromium import (
    ChromiumManager,      # Main orchestrator (same as before)
    PlatformDetector,     # Platform-specific logic
    VersionManager,       # Version compatibility
    ChromiumDownloader,   # Download utilities
    ArchiveExtractor,     # Archive handling
)

# ✅ LEGACY - Static functions still work
from quick_browser.chromium import get_chrome_version, get_chromedriver_version

def example_old_style():
    '''Example using the old style - still works!'''
    from quick_browser import BrowserConfig
    from quick_browser.chromium import ChromiumManager

    config = BrowserConfig()
    chromium_manager = ChromiumManager(config)
    chrome_path = chromium_manager.get_or_download_chromium()
    print(f"Chrome ready: {chrome_path}")

if __name__ == "__main__":
    print("🔍 Testing all import patterns...")

    # Test backward compatibility
    from quick_browser.chromium import ChromiumManager
    print("✅ ChromiumManager import works")

    # Test new modular imports
    from quick_browser.chromium import PlatformDetector, VersionManager
    print("✅ Modular imports work")

    print("🎉 All import patterns successful!")
"""

    examples_file = BASE_DIR / "examples" / "chromium_usage_examples.py"
    examples_file.parent.mkdir(exist_ok=True)
    examples_file.write_text(examples_content.strip())
    print(f"   ✓ Created usage examples: {examples_file}")


def update_main_chromium_import() -> None:
    """Update main quick_browser/__init__.py to import from new structure."""
    main_init = BASE_DIR / "quick_browser" / "__init__.py"

    if main_init.exists():
        print(f"   ✓ Main __init__.py import unchanged (backward compatible)")
    else:
        print(f"   ⚠ Main __init__.py not found at {main_init}")


def backup_original_file() -> None:
    """Backup the original chromium.py file."""
    if ORIGINAL_FILE.exists():
        backup_path = ORIGINAL_FILE.with_suffix('.py.backup')
        shutil.copy2(ORIGINAL_FILE, backup_path)
        print(f"   ✓ Backed up original file to: {backup_path}")

        # Ask user if they want to remove the original
        print("   🗑️  Remove original chromium.py after backup? (y/N): ", end="")
        remove_original = input().lower().strip()

        if remove_original in ["y", "yes"]:
            ORIGINAL_FILE.unlink()
            print(f"   ✓ Removed original file: {ORIGINAL_FILE}")
            print(f"     📦 All functionality now available via chromium/ package")
        else:
            print(f"   📁 Original file kept: {ORIGINAL_FILE}")
            print(f"     ⚠️  Note: You may have import conflicts - consider removing it manually")
    else:
        print(f"   ⚠ Original file not found at {ORIGINAL_FILE}")


def create_migration_summary() -> None:
    """Create a summary of the migration."""
    summary_text = f"""
📋 Chromium Module Refactoring Complete!

✅ Created Files:
   • {CHROMIUM_DIR}/__init__.py      - Package exports (ALL classes available!)
   • {CHROMIUM_DIR}/manager.py       - Main ChromiumManager class  
   • {CHROMIUM_DIR}/downloader.py    - Download logic
   • {CHROMIUM_DIR}/extractor.py     - Archive extraction
   • {CHROMIUM_DIR}/platform.py      - Platform detection
   • {CHROMIUM_DIR}/version.py       - Version management
   • {BASE_DIR}/examples/chromium_usage_examples.py - Usage examples

🔄 Backward Compatibility:
   • All existing imports continue to work:
     from quick_browser.chromium import ChromiumManager

   • NEW: All modular classes available as direct imports:
     from quick_browser.chromium import PlatformDetector
     from quick_browser.chromium import VersionManager  
     from quick_browser.chromium import ChromiumDownloader
     from quick_browser.chromium import ArchiveExtractor

   • Legacy static functions still work:
     from quick_browser.chromium import get_chrome_version
     from quick_browser.chromium import get_chromedriver_version

🧪 Next Steps:
   1. Test imports from project root:
      cd {BASE_DIR}
      python -c "from quick_browser.chromium import ChromiumManager; print('✅ Works!')"

   2. Run existing tests to verify compatibility:
      cd {BASE_DIR}
      python -m pytest tests/

   3. Original chromium.py handling complete!
   4. No more monolithic files - enjoy modular structure! 🎉

💡 Benefits of New Structure:
   • Single Responsibility: Each module has one clear purpose
   • Better Testing: Test individual components in isolation  
   • Easier Maintenance: Changes only affect relevant modules
   • Enhanced API: Access both high-level and low-level functionality

⚠️  Note: Original chromium.py backed up as chromium.py.backup  
📂 Working from scripts directory - paths auto-detected
📚 Usage examples created in examples/chromium_usage_examples.py
"""

    print(summary_text)


def main() -> None:
    """Main refactoring function."""
    print("🔧 Starting Chromium Module Refactoring...")
    print("=" * 60)
    print(f"📂 Script running from: {SCRIPT_DIR}")
    print(f"📂 Project root detected: {BASE_DIR}")
    print(f"🎯 Target package: {BASE_DIR / 'quick_browser'}")
    print()

    # Backup original
    backup_original_file()

    # Create structure
    create_directory_structure()

    # Create all module files
    create_init_py()
    create_platform_py()
    create_version_py()
    create_extractor_py()
    create_downloader_py()
    create_manager_py()

    # Create usage examples
    create_usage_examples()

    # Update imports (if needed)
    update_main_chromium_import()

    # Summary
    create_migration_summary()

    print("🎉 Refactoring completed successfully!")


if __name__ == "__main__":
    main()