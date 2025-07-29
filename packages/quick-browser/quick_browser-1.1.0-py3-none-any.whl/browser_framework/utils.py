"""Utility-Klassen für erweiterte Browser-Funktionalität."""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from browser_framework import BrowserFramework

logger = logging.getLogger(__name__)


class ElementWaiter:
    """Utility-Klasse für erweiterte Element-Warteschlangen."""

    def __init__(self, driver: webdriver.Chrome, default_timeout: int = 10) -> None:
        """
        Initialisiert ElementWaiter.

        Args:
            driver: WebDriver-Instanz
            default_timeout: Standard-Timeout in Sekunden
        """
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_any_element(
        self, locators: List[Tuple[str, str]], timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wartet auf eines von mehreren Elementen.

        Args:
            locators: Liste von Locator-Tupeln
            timeout: Timeout in Sekunden

        Returns:
            Erstes gefundenes Element oder None
        """
        timeout = timeout or self.default_timeout
        end_time = time.time() + timeout

        while time.time() < end_time:
            for by, value in locators:
                try:
                    element = self.driver.find_element(by, value)
                    if element.is_displayed() and element.is_enabled():
                        return element
                except NoSuchElementException:
                    continue

            time.sleep(0.1)

        return None

    def wait_for_element_text_change(
        self, locator: Tuple[str, str], initial_text: str, timeout: Optional[int] = None
    ) -> bool:
        """
        Wartet darauf, dass sich der Text eines Elements ändert.

        Args:
            locator: Element-Locator
            initial_text: Ursprünglicher Text
            timeout: Timeout in Sekunden

        Returns:
            True wenn Text sich geändert hat
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_element(*locator).text != initial_text
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False


class PerformanceMonitor:
    """Monitor für Browser-Performance."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        """
        Initialisiert PerformanceMonitor.

        Args:
            driver: WebDriver-Instanz
        """
        self.driver = driver

    def get_page_load_time(self) -> float:
        """
        Ermittelt Seitenladezeit.

        Returns:
            Ladezeit in Sekunden
        """
        navigation_start = self.driver.execute_script(
            "return window.performance.timing.navigationStart"
        )
        dom_complete = self.driver.execute_script(
            "return window.performance.timing.domComplete"
        )
        return (dom_complete - navigation_start) / 1000.0

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Ermittelt Speicherverbrauch.

        Returns:
            Dictionary mit Speicher-Informationen
        """
        try:
            memory_info = self.driver.execute_script("return window.performance.memory")
            return {
                "used_heap": memory_info.get("usedJSHeapSize", 0),
                "total_heap": memory_info.get("totalJSHeapSize", 0),
                "heap_limit": memory_info.get("jsHeapSizeLimit", 0),
            }
        except Exception:
            return {}

    def log_performance_metrics(self) -> None:
        """Loggt Performance-Metriken."""
        try:
            load_time = self.get_page_load_time()
            memory = self.get_memory_usage()

            logger.info(f"Page load time: {load_time:.2f}s")
            if memory:
                logger.info(
                    f"Memory usage: {memory['used_heap'] / 1024 / 1024:.1f}MB / "
                    f"{memory['total_heap'] / 1024 / 1024:.1f}MB"
                )
        except Exception as e:
            logger.warning(f"Failed to get performance metrics: {e}")


class BrowserHealthChecker:
    """Gesundheitsprüfung für Browser-Instanz."""

    def __init__(self, browser: BrowserFramework) -> None:
        """
        Initialisiert BrowserHealthChecker.

        Args:
            browser: BrowserFramework-Instanz
        """
        self.browser = browser

    def is_healthy(self) -> bool:
        """
        Prüft ob Browser gesund ist.

        Returns:
            True wenn Browser funktionsfähig
        """
        if not self.browser.driver:
            return False

        try:
            # Basis-Gesundheitsprüfungen
            return (
                len(self.browser.driver.window_handles) > 0
                and self.browser.driver.current_url.startswith("http")
                and self._can_execute_javascript()
            )
        except Exception:
            return False

    def _can_execute_javascript(self) -> bool:
        """Prüft ob JavaScript ausgeführt werden kann."""
        try:
            result = self.browser.driver.execute_script("return true;")
            return result is True
        except Exception:
            return False

    def get_health_report(self) -> Dict[str, Any]:
        """
        Erstellt detaillierten Gesundheitsbericht.

        Returns:
            Dictionary mit Gesundheitsinformationen
        """
        report = {
            "is_healthy": self.is_healthy(),
            "timestamp": time.time(),
            "window_count": 0,
            "current_url": "",
            "javascript_enabled": False,
            "errors": [],
        }

        if self.browser.driver:
            try:
                report["window_count"] = len(self.browser.driver.window_handles)
                report["current_url"] = self.browser.driver.current_url
                report["javascript_enabled"] = self._can_execute_javascript()
            except Exception as e:
                report["errors"].append(str(e))

        return report
