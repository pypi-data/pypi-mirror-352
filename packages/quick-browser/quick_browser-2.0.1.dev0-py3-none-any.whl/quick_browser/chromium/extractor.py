"""Archive extraction utilities for Chromium and ChromeDriver packages."""

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
