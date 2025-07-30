"""Cross-platform Chromium Download und Setup Manager."""

import logging
import platform
import subprocess
import tempfile
import zipfile
from pathlib import Path

import requests

from .config import BrowserConfig
from .download import download_with_progress
from .exceptions import DownloadError, SetupError
from .system import is_linux, is_windows, temp_console

logger = logging.getLogger(__name__)


class ChromiumManager:
    """Cross-platform Manager für Chromium-Downloads und -Setup."""

    PORTABLE_BROWSER_DIR: Path = Path(tempfile.gettempdir()) / "portable_browser"
    CHROMIUM_DIR: Path = PORTABLE_BROWSER_DIR / "chromium"
    ZIP_DIR: Path = PORTABLE_BROWSER_DIR / "zips"

    # API für ungoogled-chromium releases
    RELEASES_API: str = (
        "https://api.github.com/repos/"
        "ungoogled-software/ungoogled-chromium-{platform}/releases/latest"
    )

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialisiert den ChromiumManager.

        Args:
            config: Browser-Konfiguration
        """
        self.config = config
        self._ensure_directories()

        # System-Info loggen falls aktiviert
        if config.log_system_info:
            from .system import get_platform_info
            platform_info = get_platform_info()
            logger.info(f"System: {platform_info['system']} {platform_info['release']}")
            logger.info(f"Architecture: {platform_info['architecture']}")
            logger.info("Framework: Cross-platform mode")

    def _ensure_directories(self) -> None:
        """Erstellt notwendige Verzeichnisse."""
        self.ZIP_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMIUM_DIR.mkdir(parents=True, exist_ok=True)

    def get_or_download_chromium(self) -> Path:
        """
        Gibt Pfad zu chrome/chromium zurück, lädt bei Bedarf herunter.

        Returns:
            Pfad zu chrome/chromium executable

        Raises:
            SetupError: Bei Setup-Fehlern
        """
        try:
            if self.config.chromium_version:
                zip_path = self._download_specific_chromium()
            else:
                zip_path = self._download_latest_chromium()

            executable_path = self._extract_chromium(zip_path)
            logger.info(f"Chromium ready ({self._get_platform_name()}): {executable_path}")
            return executable_path

        except Exception as e:
            raise SetupError(f"Chromium setup failed: {e}") from e

    def _get_platform_name(self) -> str:
        """Ermittelt Plattform-Namen für ungoogled-chromium."""
        if is_windows():
            return "windows"
        elif is_linux():
            return "linux"
        else:
            raise SetupError(f"Unsupported platform: {platform.system()}")

    def _get_platform_archive_pattern(self) -> str:
        """Ermittelt Archive-Pattern für die aktuelle Plattform."""
        arch = platform.machine().lower()

        if is_windows():
            # Windows unterstützt nur x64
            if arch in ['amd64', 'x86_64']:
                return "windows_x64"
            else:
                raise SetupError(f"Unsupported Windows architecture: {arch}")

        elif is_linux():
            # Linux unterstützt x64 und ARM64
            if arch in ['x86_64', 'amd64']:
                return "linux_x64"
            elif arch in ['aarch64', 'arm64']:
                return "linux_arm64"
            else:
                raise SetupError(f"Unsupported Linux architecture: {arch}")

        else:
            raise SetupError(f"Unsupported platform: {platform.system()}")

    def _get_executable_name(self) -> str:
        """Ermittelt den Namen der ausführbaren Datei."""
        if is_windows():
            return "chrome.exe"
        else:  # Linux
            return "chrome"

    def _download_latest_chromium(self) -> Path:
        """Lädt neueste Chromium-Version für aktuelle Plattform herunter."""
        platform_name = self._get_platform_name()
        api_url = self.RELEASES_API.format(platform=platform_name)

        logger.info(f"Fetching latest release info for {platform_name}...")

        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise DownloadError(f"Failed to fetch release info: {e}") from e

        # Suche nach Asset für aktuelle Plattform/Architektur
        platform_pattern = self._get_platform_archive_pattern()
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
                f"No {platform_pattern} Chromium asset found.\n"
                f"Available assets: {available_assets}"
            )

        zip_path = self.ZIP_DIR / asset["name"]

        if not zip_path.exists():
            logger.info(f"Downloading {asset['name']}...")

            if self.config.show_console:
                with temp_console("Chromium‑Download"):
                    download_with_progress(
                        asset["browser_download_url"],
                        zip_path,
                        self.config.download_timeout,
                    )
            else:
                download_with_progress(
                    asset["browser_download_url"],
                    zip_path,
                    self.config.download_timeout,
                )
        else:
            logger.info("Chromium archive already exists")

        return zip_path

    def _download_specific_chromium(self) -> Path:
        """Lädt spezifische Chromium-Version für aktuelle Plattform herunter."""
        if not self.config.chromium_version:
            raise ValueError("Chromium version not specified")

        version = self.config.chromium_version
        platform_name = self._get_platform_name()
        platform_pattern = self._get_platform_archive_pattern()

        # Tag-Format ist unterschiedlich für verschiedene Plattformen
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

        zip_path = self.ZIP_DIR / filename

        if not zip_path.exists():
            logger.info(f"Downloading Chromium {version} ({platform_pattern})...")
            try:
                if self.config.show_console:
                    with temp_console("Chromium‑Download"):
                        download_with_progress(
                            url, zip_path, self.config.download_timeout
                        )
                else:
                    download_with_progress(url, zip_path, self.config.download_timeout)
            except DownloadError as e:
                raise DownloadError(
                    f"Failed to download Chromium {version} ({platform_pattern}): {e}"
                ) from e
        else:
            logger.info("Chromium archive already exists")

        return zip_path

    def _extract_chromium(self, archive_path: Path) -> Path:
        """Extrahiert Chromium aus Archive-Datei."""
        extract_dir = self.CHROMIUM_DIR / archive_path.stem
        executable_name = self._get_executable_name()
        executable_path = extract_dir / executable_name

        if executable_path.exists():
            logger.info(f"Chromium already extracted: {executable_path}")
            return executable_path

        logger.info("Extracting Chromium...")
        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            if archive_path.suffix == '.zip':
                self._extract_zip(archive_path, extract_dir)
            elif archive_path.suffix == '.xz':
                self._extract_tar_xz(archive_path, extract_dir)
            else:
                raise SetupError(f"Unsupported archive format: {archive_path.suffix}")

        except Exception as e:
            raise SetupError(f"Extraction failed: {e}") from e

        # Suche nach ausführbarer Datei
        for exe_path in extract_dir.rglob(executable_name):
            if exe_path.is_file():
                # Unter Linux ausführbare Berechtigung setzen
                if is_linux():
                    exe_path.chmod(0o755)
                return exe_path

        raise SetupError(f"{executable_name} not found after extraction")

    def _extract_zip(self, archive_path: Path, extract_dir: Path) -> None:
        """Extrahiert ZIP-Datei."""
        try:
            with zipfile.ZipFile(archive_path) as zip_file:
                zip_file.extractall(extract_dir)
        except zipfile.BadZipFile as e:
            raise SetupError(f"Invalid ZIP file: {e}") from e

    def _extract_tar_xz(self, archive_path: Path, extract_dir: Path) -> None:
        """Extrahiert TAR.XZ-Datei (Linux)."""
        import tarfile

        try:
            with tarfile.open(archive_path, 'r:xz') as tar_file:
                tar_file.extractall(extract_dir)
        except tarfile.TarError as e:
            raise SetupError(f"Invalid TAR.XZ file: {e}") from e

    @staticmethod
    def get_chrome_version(chrome_exe_path: Path) -> str:
        """
        Ermittelt Chrome-Version cross-platform.

        Args:
            chrome_exe_path: Pfad zu chrome/chromium executable

        Returns:
            Versions-String

        Raises:
            SetupError: Bei Versionserkennung-Fehlern
        """
        try:
            if is_windows():
                return ChromiumManager._get_chrome_version_windows(chrome_exe_path)
            else:  # Linux
                return ChromiumManager._get_chrome_version_linux(chrome_exe_path)
        except Exception as e:
            raise SetupError(f"Failed to get Chrome version: {e}") from e

    @staticmethod
    def _get_chrome_version_windows(chrome_exe_path: Path) -> str:
        """Windows-spezifische Version-Ermittlung."""
        try:
            import win32api
            info = win32api.GetFileVersionInfo(str(chrome_exe_path), "\\")
            ms: int = info["FileVersionMS"]
            ls: int = info["FileVersionLS"]
            return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        except ImportError:
            # Fallback wenn win32api nicht verfügbar
            return ChromiumManager._get_chrome_version_subprocess(chrome_exe_path)

    @staticmethod
    def _get_chrome_version_linux(chrome_exe_path: Path) -> str:
        """Linux-spezifische Version-Ermittlung."""
        return ChromiumManager._get_chrome_version_subprocess(chrome_exe_path)

    @staticmethod
    def _get_chrome_version_subprocess(chrome_exe_path: Path) -> str:
        """Version-Ermittlung über Subprocess (cross-platform fallback)."""
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
                    if part.count('.') >= 2:  # Version format X.Y.Z.W
                        return part

            raise SetupError(f"Could not parse version from: {result.stdout}")

        except subprocess.TimeoutExpired:
            raise SetupError("Chrome version check timed out")
        except subprocess.SubprocessError as e:
            raise SetupError(f"Failed to get Chrome version via subprocess: {e}")

    @staticmethod
    def get_chromedriver_version(chrome_version: str) -> str:
        """
        Ermittelt die passende ChromeDriver-Version für eine Chrome-Version.

        Args:
            chrome_version: Chrome-Version (z.B. "136.0.7103.113")

        Returns:
            ChromeDriver-Version (z.B. "136.0.7103")
        """
        try:
            # Sichere Extraktion der ersten drei Versionsteile
            version_parts = chrome_version.split(".")
            # Wir benötigen nur major.minor.build (die ersten drei Teile)
            if len(version_parts) >= 3:
                return ".".join(version_parts[:3])
            else:
                # Fallback, wenn weniger als 3 Teile vorhanden sind
                return chrome_version
        except Exception as e:
            logger.warning(f"Fehler bei Ermittlung der ChromeDriver-Version: {e}")
            # Im Zweifelsfall die komplette Version zurückgeben
            return chrome_version
