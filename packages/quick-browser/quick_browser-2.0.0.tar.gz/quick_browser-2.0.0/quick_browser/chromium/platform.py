"""Platform detection and platform-specific utilities for Chromium management."""

import platform
from typing import Any, Dict

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
