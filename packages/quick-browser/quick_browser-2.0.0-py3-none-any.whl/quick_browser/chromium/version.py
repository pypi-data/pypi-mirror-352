"""Version management and compatibility checking for Chromium and ChromeDriver."""

import logging
import subprocess
from pathlib import Path

from ..exceptions import SetupError
from ..system import is_windows

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

            # Get version info - use correct API format
            info = win32api.GetFileVersionInfo(str(chrome_exe_path), "\\")

            # Extract version numbers from the info structure
            if isinstance(info, dict) and "FileVersionMS" in info and "FileVersionLS" in info:
                ms: int = info["FileVersionMS"]
                ls: int = info["FileVersionLS"]
                return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
            else:
                # Fallback if info structure is unexpected
                logger.warning("Unexpected GetFileVersionInfo result, using subprocess fallback")
                return VersionManager._get_chrome_version_subprocess(chrome_exe_path)

        except ImportError:
            # win32api not available - use subprocess
            logger.info("win32api not available, using subprocess method")
            return VersionManager._get_chrome_version_subprocess(chrome_exe_path)
        except Exception as e:
            # Any other error - fallback to subprocess
            logger.warning(f"win32api method failed: {e}, using subprocess fallback")
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
                timeout=15  # Increased timeout for slower systems
            )

            if result.returncode == 0:
                # Parse version from output like "Chromium 120.0.6099.109" or "Google Chrome 120.0.6099.109"
                version_line = result.stdout.strip()
                logger.debug(f"Chrome version output: {version_line}")

                # Split and find version pattern
                parts = version_line.split()
                for part in parts:
                    # Look for version pattern: at least 3 numbers separated by dots
                    if part.count(".") >= 2 and part.replace(".", "").replace("-", "").isdigit():
                        logger.info(f"Detected Chrome version: {part}")
                        return part

                # Alternative parsing: look for numbers after common browser names
                version_line_lower = version_line.lower()
                if "chromium" in version_line_lower or "chrome" in version_line_lower:
                    # Try to extract version with regex
                    import re
                    version_match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)?)', version_line)
                    if version_match:
                        version = version_match.group(1)
                        logger.info(f"Detected Chrome version via regex: {version}")
                        return version

            # If we get here, parsing failed
            error_msg = f"Could not parse version from output: '{result.stdout}'"
            if result.stderr:
                error_msg += f", stderr: '{result.stderr}'"
            raise SetupError(error_msg)

        except subprocess.TimeoutExpired:
            raise SetupError(f"Chrome version check timed out for {chrome_exe_path}")
        except subprocess.SubprocessError as e:
            raise SetupError(f"Failed to get Chrome version via subprocess: {e}")
        except Exception as e:
            raise SetupError(f"Unexpected error getting Chrome version: {e}")

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
                driver_version = ".".join(version_parts[:3])
                logger.debug(f"Chrome {chrome_version} -> ChromeDriver {driver_version}")
                return driver_version
            else:
                # Fallback if less than 3 parts available
                logger.warning(f"Unusual Chrome version format: {chrome_version}")
                return chrome_version
        except Exception as e:
            logger.warning(f"Error determining ChromeDriver version: {e}")
            # In doubt, return complete version
            return chrome_version
