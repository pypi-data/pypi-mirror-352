"""Profile management utilities for browser framework."""

import logging
import random
import shutil
import string
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class ProfileManager:
    """Manager for browser profile creation and cleanup."""

    def __init__(self, cleanup_enabled: bool = True) -> None:
        """
        Initialize profile manager.

        Args:
            cleanup_enabled: Whether to clean up profiles on exit
        """
        self.cleanup_enabled = cleanup_enabled
        self.created_profiles = []

    def create_random_profile_dir(self) -> Path:
        """
        Create temporary profile directory.

        Returns:
            Path to profile directory
        """
        name = "chrome_profile_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        profile_path = Path(tempfile.gettempdir()) / name
        profile_path.mkdir(exist_ok=True)

        # Track for cleanup
        self.created_profiles.append(profile_path)

        logger.debug(f"Created profile directory: {profile_path}")
        return profile_path

    def cleanup_profile(self, profile_dir: Path) -> None:
        """
        Clean up a specific profile directory.

        Args:
            profile_dir: Profile directory to clean up
        """
        if not self.cleanup_enabled:
            logger.debug(f"Profile cleanup disabled, keeping: {profile_dir}")
            return

        try:
            if profile_dir.exists():
                shutil.rmtree(profile_dir, ignore_errors=True)
                logger.debug(f"Cleaned up profile directory: {profile_dir}")

                # Remove from tracking
                if profile_dir in self.created_profiles:
                    self.created_profiles.remove(profile_dir)
        except Exception as e:
            logger.warning(f"Error cleaning up profile directory {profile_dir}: {e}")

    def cleanup_all_profiles(self) -> None:
        """Clean up all tracked profile directories."""
        for profile_dir in self.created_profiles.copy():
            self.cleanup_profile(profile_dir)

    def __del__(self) -> None:
        """Cleanup profiles on object destruction."""
        self.cleanup_all_profiles()
