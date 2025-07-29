"""Kern-Framework für Browser-Automatisierung - 64-bit only."""

import json
import logging
import random
import shutil
import string
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Optional, Tuple
from urllib.request import urlopen

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from .chromium import ChromiumManager
from .config import BrowserConfig
from .download import download_with_progress
from .exceptions import DownloadError, SetupError
from .system import temp_console

logger = logging.getLogger(__name__)


class BrowserFramework:
    """
    Kern-Framework für Browser-Automatisierung - 64-bit only.
    """

    def __init__(self, config: BrowserConfig) -> None:
        """
        Initialisiert das BrowserFramework.

        Args:
            config: Browser-Konfiguration
        """
        self.config = config
        self.profile_dir = self._create_random_profile_dir()
        self.chromium_manager = ChromiumManager(config)
        self.chrome_exe: Optional[Path] = None
        self.driver_path: Optional[str] = None
        self.driver: Optional[webdriver.Chrome] = None

    def __enter__(self) -> "BrowserFramework":
        """Context Manager Entry."""
        self.setup()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context Manager Exit."""
        self.quit()

    def setup(self) -> None:
        """
        Richtet Browser ein durch Download und Initialisierung.

        Raises:
            SetupError: Bei Setup-Fehlern
        """
        try:
            self.chrome_exe = self.chromium_manager.get_or_download_chromium()
            self.driver_path = self._ensure_driver()
            self.driver = self._create_driver()
            logger.info("Browser setup completed successfully (64-bit)")
        except Exception as e:
            logger.error(f"Browser setup failed: {e}")
            self._log_troubleshooting_info()
            raise SetupError(f"Browser setup failed: {e}") from e

    def _log_troubleshooting_info(self) -> None:
        """Loggt vereinfachte Informationen zur Fehlerbehebung."""
        logger.error("=== TROUBLESHOOTING INFORMATION ===")
        logger.error(f"Chrome executable: {self.chrome_exe}")
        logger.error(f"ChromeDriver: {self.driver_path}")
        logger.error("Framework is configured for 64-bit only")
        logger.error("=== END TROUBLESHOOTING INFO ===")

    def _ensure_driver(self) -> str:
        """
        Stellt sicher, dass ChromeDriver installiert ist (64-bit only).

        Returns:
            Pfad zum ChromeDriver

        Raises:
            SetupError: Bei Driver-Setup-Fehlern
        """
        if not self.chrome_exe:
            raise SetupError("Chrome executable not initialized")

        try:
            # Bestimme ChromeDriver Version
            if (
                self.config.driver_version
                and self.config.driver_version.lower() != "latest"
            ):
                driver_version = self.config.driver_version
                logger.info(f"Using specified ChromeDriver version: {driver_version}")
            else:
                chrome_version = ChromiumManager.get_chrome_version(self.chrome_exe)
                driver_version = self._get_compatible_chromedriver_version(
                    chrome_version
                )
                logger.info(
                    f"Auto-detected ChromeDriver version: {driver_version} for Chrome {chrome_version}"
                )

            # Lade ChromeDriver direkt herunter
            driver_path = self._download_chromedriver_direct(driver_version)
            logger.info(f"ChromeDriver ready: {driver_path}")
            return driver_path

        except Exception as e:
            raise SetupError(f"ChromeDriver setup failed: {e}") from e

    @staticmethod
    def _get_compatible_chromedriver_version(chrome_version: str) -> str:
        """
        Ermittelt die kompatible ChromeDriver Version für eine Chrome Version.

        Args:
            chrome_version: Chrome Version (z.B. "120.0.6099.109")

        Returns:
            Kompatible ChromeDriver Version

        Raises:
            SetupError: Wenn keine kompatible Version gefunden wird
        """
        try:
            # Extrahiere Major Version
            major_version = chrome_version.split(".")[0]

            # Lade verfügbare Versionen von Chrome for Testing API
            url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())

            # Suche nach der neuesten Version für diese Major Version
            compatible_versions = []
            for version_info in data.get("versions", []):
                version = version_info.get("version", "")
                if version.startswith(f"{major_version}."):
                    # Prüfe ob ChromeDriver für win64 verfügbar ist
                    downloads = version_info.get("downloads", {})
                    chromedriver_downloads = downloads.get("chromedriver", [])

                    for download in chromedriver_downloads:
                        if download.get("platform") == "win64":
                            compatible_versions.append(version)
                            break

            if not compatible_versions:
                raise SetupError(
                    f"No compatible ChromeDriver found for Chrome {chrome_version}"
                )

            # Nimm die neueste kompatible Version
            latest_version = max(
                compatible_versions, key=lambda v: [int(x) for x in v.split(".")]
            )
            return latest_version

        except Exception as e:
            logger.warning(f"Failed to get compatible ChromeDriver version: {e}")
            # Fallback: verwende Chrome Version als ChromeDriver Version
            return chrome_version

    def _download_chromedriver_direct(self, version: str) -> str:
        """
        Lädt ChromeDriver direkt von Chrome for Testing herunter.

        Args:
            version: ChromeDriver Version

        Returns:
            Pfad zur chromedriver.exe

        Raises:
            SetupError: Bei Download-Fehlern
        """
        try:
            # Verwende das konsistente portable_browser Verzeichnis vom ChromiumManager
            portable_browser_dir = self.chromium_manager.PORTABLE_BROWSER_DIR
            chromedriver_dir = portable_browser_dir / f"chromedriver-{version}"
            chromedriver_exe = chromedriver_dir / "chromedriver.exe"

            # Prüfe ob bereits vorhanden
            if chromedriver_exe.exists():
                logger.info(f"ChromeDriver already exists: {chromedriver_exe}")
                return str(chromedriver_exe)

            # Erstelle Verzeichnis
            chromedriver_dir.mkdir(parents=True, exist_ok=True)

            # Ermittle Download-URL
            download_url = self._get_chromedriver_download_url(version)

            # Lade ZIP-Datei mit Fortschrittsanzeige herunter
            zip_path = chromedriver_dir / "chromedriver.zip"
            logger.info(f"Downloading ChromeDriver {version}...")

            try:
                # Bedingter Console-Aufruf basierend auf show_console Flag
                if self.config.show_console:
                    with temp_console("ChromeDriver‑Download"):
                        download_with_progress(
                            download_url, zip_path, self.config.download_timeout
                        )
                else:
                    # Direkter Download ohne Console
                    download_with_progress(
                        download_url, zip_path, self.config.download_timeout
                    )
            except DownloadError as e:
                raise SetupError(
                    f"Failed to download ChromeDriver {version}: {e}"
                ) from e

            # Extrahiere ZIP
            logger.info("Extracting ChromeDriver...")
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(chromedriver_dir)
            except zipfile.BadZipFile as e:
                raise SetupError(f"Invalid ChromeDriver ZIP file: {e}") from e

            # Lösche ZIP-Datei
            zip_path.unlink()

            # Finde chromedriver.exe in extrahierten Dateien
            for exe_path in chromedriver_dir.rglob("chromedriver.exe"):
                # Verschiebe chromedriver.exe in das Hauptverzeichnis falls nötig
                if exe_path != chromedriver_exe:
                    shutil.move(str(exe_path), str(chromedriver_exe))
                    # Lösche leere Unterverzeichnisse
                    if exe_path.parent != chromedriver_dir and not any(
                        exe_path.parent.iterdir()
                    ):
                        exe_path.parent.rmdir()
                break

            if not chromedriver_exe.exists():
                raise SetupError("chromedriver.exe not found in downloaded archive")

            logger.info(f"ChromeDriver downloaded successfully: {chromedriver_exe}")
            return str(chromedriver_exe)

        except Exception as e:
            if isinstance(e, (SetupError, DownloadError)):
                raise
            raise SetupError(f"Failed to download ChromeDriver: {e}") from e

    @staticmethod
    def _get_chromedriver_download_url(version: str) -> str:
        """
        Ermittelt die Download-URL für ChromeDriver von Chrome for Testing.

        Args:
            version: ChromeDriver Version

        Returns:
            Download-URL für win64 ChromeDriver

        Raises:
            SetupError: Wenn URL nicht gefunden wird
        """
        try:
            # Lade Download-Informationen für die spezifische Version
            url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            with urlopen(url) as response:
                data = json.loads(response.read().decode())

            # Suche nach der gewünschten Version
            for version_info in data.get("versions", []):
                if version_info.get("version") == version:
                    downloads = version_info.get("downloads", {})
                    chromedriver_downloads = downloads.get("chromedriver", [])

                    # Suche nach win64 Download
                    for download in chromedriver_downloads:
                        if download.get("platform") == "win64":
                            download_url = download.get("url")
                            if download_url:
                                logger.debug(
                                    f"Found ChromeDriver download URL from API: {download_url}"
                                )
                                return download_url

            # Fallback: verwende direkte URL-Struktur
            fallback_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip"
            logger.warning(
                f"Version {version} not found in API, using fallback URL: {fallback_url}"
            )
            return fallback_url

        except Exception as e:
            # Letzter Fallback
            fallback_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/win64/chromedriver-win64.zip"
            logger.warning(
                f"Failed to get download URL from API: {e}, using fallback: {fallback_url}"
            )
            return fallback_url

    @staticmethod
    def _create_random_profile_dir() -> Path:
        """
        Erstellt temporäres Profil-Verzeichnis.

        Returns:
            Pfad zum Profil-Verzeichnis
        """
        name = "chrome_profile_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        profile_path = Path(tempfile.gettempdir()) / name
        profile_path.mkdir(exist_ok=True)
        return profile_path

    def _create_driver(self) -> webdriver.Chrome:
        """
        Erstellt und konfiguriert WebDriver.

        Returns:
            Konfigurierte Chrome WebDriver-Instanz

        Raises:
            SetupError: Bei Driver-Erstellung-Fehlern
        """
        if not self.chrome_exe or not self.driver_path:
            raise SetupError("Chrome executable or driver path not initialized")

        try:
            logger.info(f"Creating WebDriver with Chrome: {self.chrome_exe}")
            logger.info(f"Using ChromeDriver: {self.driver_path}")

            options = Options()
            options.binary_location = str(self.chrome_exe)
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument(
                "--kiosk" if self.config.kiosk else "--start-maximized"
            )

            if self.config.headless:
                options.add_argument("--headless=new")

            # Performance-Flags hinzufügen
            for flag in self.config.performance_flags:
                options.add_argument(flag)

            # Browser-Präferenzen setzen
            options.add_experimental_option("prefs", self.config.browser_prefs)
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option(
                "excludeSwitches", ["enable-automation", "enable-logging"]
            )

            service = Service(self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            # Timeouts setzen
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.set_script_timeout(self.config.script_timeout)
            driver.implicitly_wait(self.config.implicit_wait)

            logger.info("WebDriver created successfully")
            return driver

        except WebDriverException as e:
            raise SetupError(f"Failed to create WebDriver: {e}") from e
        except Exception as e:
            raise SetupError(f"Failed to create WebDriver: {e}") from e

    def safe_click(self, by: str, value: str, timeout: int = 5) -> bool:
        """
        Sicherer Click mit Timeout-Behandlung.

        Args:
            by: Locator-Strategie
            value: Locator-Wert
            timeout: Timeout in Sekunden

        Returns:
            True bei Erfolg, False bei Timeout
        """
        try:
            self._wait_and_click((by, value), timeout)
            return True
        except TimeoutException:
            logger.warning(f"Timeout beim Klicken auf Element: {by}={value}")
            return False
        except Exception as e:
            logger.error(f"Fehler beim Klicken auf Element: {e}")
            return False

    def click_by_id(self, element_id: str, timeout: Optional[int] = None) -> WebElement:
        """Klickt Element per ID."""
        return self._wait_and_click(
            (By.ID, element_id), timeout or self.config.element_timeout
        )

    def click_by_css(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """Klickt Element per CSS-Selektor."""
        return self._wait_and_click(
            (By.CSS_SELECTOR, selector), timeout or self.config.element_timeout
        )

    def send_keys_by_name(
        self, name: str, keys: str, timeout: Optional[int] = None
    ) -> WebElement:
        """
        Sendet Tasten an Element per Name.

        Args:
            name: Name-Attribut
            keys: Zu sendende Tasten
            timeout: Timeout in Sekunden

        Returns:
            Das Element
        """
        if not self.driver:
            raise SetupError("Driver not initialized")

        element = WebDriverWait(
            self.driver, timeout or self.config.element_timeout
        ).until(expected_conditions.element_to_be_clickable((By.NAME, name)))
        element.send_keys(keys)
        return element

    def _wait_and_click(self, locator: Tuple[str, str], timeout: int) -> WebElement:
        """
        Wartet auf Element und klickt es.

        Args:
            locator: Tuple aus Strategie und Wert
            timeout: Timeout in Sekunden

        Returns:
            Das geklickte Element
        """
        if not self.driver:
            raise SetupError("Driver not initialized")

        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable(locator)
        )
        element.click()
        return element

    def remove_elements_by_ids(self, element_ids: Tuple[str, ...]) -> None:
        """
        Entfernt mehrere Elemente per ID.

        Args:
            element_ids: Tuple von Element-IDs
        """
        if not self.driver:
            return

        for element_id in element_ids:
            try:
                self.driver.execute_script(
                    "var el = document.getElementById(arguments[0]); "
                    "if (el) { el.remove(); }",
                    element_id,
                )
                logger.debug(f"Removed element: {element_id}")
            except Exception as e:
                logger.warning(f"Failed to remove element {element_id}: {e}")

    def scroll_to_element(self, selector: str, behavior: str = "smooth") -> None:
        """
        Scrollt zu einem Element.

        Args:
            selector: CSS-Selektor des Elements
            behavior: Scroll-Verhalten ('smooth' oder 'instant')
        """
        if not self.driver:
            return

        scroll_script = f"""
        const element = document.querySelector(arguments[0]);
        if (element) {{
            element.scrollIntoView({{ behavior: '{behavior}', block: 'center' }});
        }}
        """
        self.driver.execute_script(scroll_script, selector)

    def quit(self) -> None:
        """Beendet WebDriver und räumt auf."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")

        if self.config.profile_cleanup:
            try:
                shutil.rmtree(self.profile_dir, ignore_errors=True)
                logger.debug("Profile directory cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up profile directory: {e}")
