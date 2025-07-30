"""Troubleshooting and debugging utilities for browser framework."""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class TroubleshootingHelper:
    """Helper class for browser framework troubleshooting and debugging."""

    @staticmethod
    def log_troubleshooting_info(chrome_exe: Optional[Path], driver_path: Optional[str]) -> None:
        """Log cross-platform information for troubleshooting."""
        from ..system import get_platform_info

        platform_info = get_platform_info()
        logger.error("=== TROUBLESHOOTING INFORMATION ===")
        logger.error(f"Platform: {platform_info['system']} {platform_info['release']}")
        logger.error(f"Architecture: {platform_info['architecture']}")
        logger.error(f"Chrome executable: {chrome_exe}")
        logger.error(f"ChromeDriver: {driver_path}")
        logger.error("Framework: Cross-platform mode")
        logger.error("=== END TROUBLESHOOTING INFO ===")

    @staticmethod
    def get_platform_name() -> str:
        """Get platform name for logging."""
        from ..system import is_linux, is_windows

        if is_windows():
            return "Windows"
        elif is_linux():
            return "Linux"
        else:
            return "Unknown"

    @staticmethod
    def validate_paths(chrome_exe: Optional[Path], driver_path: Optional[str]) -> list[str]:
        """
        Validate browser and driver paths.

        Returns:
            List of validation errors
        """
        errors = []

        if chrome_exe and not chrome_exe.exists():
            errors.append(f"Chrome executable not found: {chrome_exe}")

        if driver_path and not Path(driver_path).exists():
            errors.append(f"ChromeDriver not found: {driver_path}")

        return errors
