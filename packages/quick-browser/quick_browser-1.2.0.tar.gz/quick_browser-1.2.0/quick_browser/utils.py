"""Cross-platform Utility-Klassen für erweiterte Browser-Funktionalität."""

import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from .core import BrowserFramework

logger = logging.getLogger(__name__)


class ElementWaiter:
    """Cross-platform Utility-Klasse für erweiterte Element-Warteschlangen."""

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

    def wait_for_element_to_disappear(
        self, locator: Tuple[str, str], timeout: Optional[int] = None
    ) -> bool:
        """
        Wartet darauf, dass ein Element verschwindet.

        Args:
            locator: Element-Locator
            timeout: Timeout in Sekunden

        Returns:
            True wenn Element verschwunden ist
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until_not(
                lambda d: d.find_element(*locator).is_displayed()
            )
            return True
        except (TimeoutException, NoSuchElementException):
            # Element ist bereits nicht da - das ist gut
            return True

    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wartet auf vollständiges Laden der Seite.

        Args:
            timeout: Timeout in Sekunden

        Returns:
            True wenn Seite geladen ist
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False

    def wait_for_ajax_complete(
        self, timeout: Optional[int] = None, jquery: bool = True
    ) -> bool:
        """
        Wartet auf Abschluss von AJAX-Requests.

        Args:
            timeout: Timeout in Sekunden
            jquery: Prüfe auch auf jQuery AJAX

        Returns:
            True wenn AJAX abgeschlossen ist
        """
        timeout = timeout or self.default_timeout

        try:
            if jquery:
                # Warte auf jQuery AJAX
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script(
                        "return typeof jQuery !== 'undefined' ? jQuery.active === 0 : true"
                    )
                )

            # Warte auf native XMLHttpRequest
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    """
                    var requests = window.openHTTPRequests || 0;
                    return requests === 0;
                    """
                )
            )
            return True
        except TimeoutException:
            return False


class PerformanceMonitor:
    """Cross-platform Monitor für Browser-Performance."""

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
        try:
            navigation_start = self.driver.execute_script(
                "return window.performance.timing.navigationStart"
            )
            dom_complete = self.driver.execute_script(
                "return window.performance.timing.domComplete"
            )
            return (dom_complete - navigation_start) / 1000.0
        except Exception as e:
            logger.warning(f"Could not get page load time: {e}")
            return 0.0

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Ermittelt Speicherverbrauch (cross-platform).

        Returns:
            Dictionary mit Speicher-Informationen
        """
        try:
            memory_info = self.driver.execute_script(
                """
                if ('memory' in performance) {
                    return {
                        usedJSHeapSize: performance.memory.usedJSHeapSize,
                        totalJSHeapSize: performance.memory.totalJSHeapSize,
                        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
                """
            )

            if memory_info:
                return {
                    "used_heap": memory_info.get("usedJSHeapSize", 0),
                    "total_heap": memory_info.get("totalJSHeapSize", 0),
                    "heap_limit": memory_info.get("jsHeapSizeLimit", 0),
                }
            else:
                # Fallback für Browser ohne Memory API
                return {
                    "used_heap": 0,
                    "total_heap": 0,
                    "heap_limit": 0,
                }
        except Exception as e:
            logger.warning(f"Could not get memory usage: {e}")
            return {}

    def get_network_timing(self) -> Dict[str, Any]:
        """
        Ermittelt Netzwerk-Timing-Informationen.

        Returns:
            Dictionary mit Timing-Informationen
        """
        try:
            timing = self.driver.execute_script(
                """
                var timing = performance.getEntriesByType('navigation')[0];
                if (timing) {
                    return {
                        dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                        tcpConnect: timing.connectEnd - timing.connectStart,
                        request: timing.responseStart - timing.requestStart,
                        response: timing.responseEnd - timing.responseStart,
                        domParsing: timing.domContentLoadedEventStart - timing.responseEnd,
                        resourceLoad: timing.loadEventStart - timing.domContentLoadedEventEnd
                    };
                }
                return null;
                """
            )

            return timing or {}
        except Exception as e:
            logger.warning(f"Could not get network timing: {e}")
            return {}

    def get_resource_timing(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ermittelt Resource-Timing für die langsamsten Ressourcen.

        Args:
            limit: Anzahl der Ressourcen die zurückgegeben werden

        Returns:
            Liste der langsamsten Ressourcen
        """
        try:
            resources = self.driver.execute_script(
                f"""
                var resources = performance.getEntriesByType('resource');
                return resources
                    .map(function(resource) {{
                        return {{
                            name: resource.name,
                            duration: resource.duration,
                            size: resource.transferSize || 0,
                            type: resource.initiatorType
                        }};
                    }})
                    .sort(function(a, b) {{ return b.duration - a.duration; }})
                    .slice(0, {limit});
                """
            )

            return resources or []
        except Exception as e:
            logger.warning(f"Could not get resource timing: {e}")
            return []

    def log_performance_metrics(self) -> None:
        """Loggt umfassende Performance-Metriken."""
        try:
            load_time = self.get_page_load_time()
            memory = self.get_memory_usage()
            network = self.get_network_timing()

            logger.info("📊 Performance Metrics:")
            logger.info(f"   Page load time: {load_time:.2f}s")

            if memory:
                memory_mb = memory['used_heap'] / 1024 / 1024
                total_mb = memory['total_heap'] / 1024 / 1024
                logger.info(f"   Memory usage: {memory_mb:.1f}MB / {total_mb:.1f}MB")

            if network:
                logger.info(f"   DNS lookup: {network.get('dnsLookup', 0):.0f}ms")
                logger.info(f"   TCP connect: {network.get('tcpConnect', 0):.0f}ms")
                logger.info(f"   Request: {network.get('request', 0):.0f}ms")
                logger.info(f"   Response: {network.get('response', 0):.0f}ms")

        except Exception as e:
            logger.warning(f"Failed to log performance metrics: {e}")

    def create_performance_report(self) -> Dict[str, Any]:
        """
        Erstellt detaillierten Performance-Report.

        Returns:
            Dictionary mit Performance-Daten
        """
        report = {
            "timestamp": time.time(),
            "url": self.driver.current_url,
            "load_time": self.get_page_load_time(),
            "memory": self.get_memory_usage(),
            "network": self.get_network_timing(),
            "slow_resources": self.get_resource_timing(5),
        }

        return report


class BrowserHealthChecker:
    """Cross-platform Gesundheitsprüfung für Browser-Instanz."""

    def __init__(self, browser_framework: 'BrowserFramework') -> None:
        """
        Initialisiert BrowserHealthChecker.

        Args:
            browser_framework: BrowserFramework-Instanz
        """
        self.browser = browser_framework

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
                self._has_active_windows()
                and self._has_valid_url()
                and self._can_execute_javascript()
                and self._is_responsive()
            )
        except Exception:
            return False

    def _has_active_windows(self) -> bool:
        """Prüft ob aktive Browser-Fenster vorhanden sind."""
        try:
            return len(self.browser.driver.window_handles) > 0
        except Exception:
            return False

    def _has_valid_url(self) -> bool:
        """Prüft ob aktuelle URL gültig ist."""
        try:
            url = self.browser.driver.current_url
            return url and (url.startswith("http") or url.startswith("file") or url == "data:,")
        except Exception:
            return False

    def _can_execute_javascript(self) -> bool:
        """Prüft ob JavaScript ausgeführt werden kann."""
        try:
            result = self.browser.driver.execute_script("return true;")
            return result is True
        except Exception:
            return False

    def _is_responsive(self) -> bool:
        """Prüft ob Browser responsive ist."""
        try:
            # Einfacher Responsiveness-Test
            start_time = time.time()
            self.browser.driver.execute_script("return document.readyState;")
            response_time = time.time() - start_time

            # Browser sollte innerhalb von 5 Sekunden antworten
            return response_time < 5.0
        except Exception:
            return False

    def get_health_report(self) -> Dict[str, Any]:
        """
        Erstellt detaillierten Gesundheitsbericht.

        Returns:
            Dictionary mit Gesundheitsinformationen
        """
        report = {
            "is_healthy": False,
            "timestamp": time.time(),
            "window_count": 0,
            "current_url": "",
            "javascript_enabled": False,
            "responsive": False,
            "errors": [],
            "warnings": [],
        }

        if not self.browser.driver:
            report["errors"].append("WebDriver not initialized")
            return report

        try:
            # Window-Count
            report["window_count"] = len(self.browser.driver.window_handles)
            if report["window_count"] == 0:
                report["errors"].append("No active browser windows")

            # Current URL
            report["current_url"] = self.browser.driver.current_url
            if not self._has_valid_url():
                report["warnings"].append("Invalid or missing URL")

            # JavaScript
            report["javascript_enabled"] = self._can_execute_javascript()
            if not report["javascript_enabled"]:
                report["errors"].append("JavaScript execution failed")

            # Responsiveness
            report["responsive"] = self._is_responsive()
            if not report["responsive"]:
                report["warnings"].append("Browser is slow to respond")

            # Overall health
            report["is_healthy"] = self.is_healthy()

        except Exception as e:
            report["errors"].append(f"Health check failed: {str(e)}")

        return report

    def diagnose_issues(self) -> List[str]:
        """
        Diagnostiziert Browser-Probleme und gibt Lösungsvorschläge.

        Returns:
            Liste von Diagnose-Nachrichten
        """
        diagnoses = []

        try:
            if not self.browser.driver:
                diagnoses.append("🔴 Browser not initialized - call setup() first")
                return diagnoses

            health_report = self.get_health_report()

            if health_report["window_count"] == 0:
                diagnoses.append("🔴 No browser windows - browser may have crashed")

            if not health_report["javascript_enabled"]:
                diagnoses.append("🔴 JavaScript disabled or broken - check browser settings")

            if not health_report["responsive"]:
                diagnoses.append("⚠️ Browser is slow - may be under heavy load")

            if health_report["errors"]:
                for error in health_report["errors"]:
                    diagnoses.append(f"🔴 {error}")

            if health_report["warnings"]:
                for warning in health_report["warnings"]:
                    diagnoses.append(f"⚠️ {warning}")

            if health_report["is_healthy"]:
                diagnoses.append("✅ Browser is healthy")

        except Exception as e:
            diagnoses.append(f"🔴 Diagnosis failed: {e}")

        return diagnoses

    def auto_heal(self) -> bool:
        """
        Versucht automatische Browser-Reparatur.

        Returns:
            True wenn Reparatur erfolgreich
        """
        try:
            if not self.browser.driver:
                logger.info("🔧 Attempting to reinitialize browser...")
                self.browser.setup()
                return self.is_healthy()

            # Versuche Browser-Refresh bei Problemen
            if not self._is_responsive():
                logger.info("🔧 Browser unresponsive, attempting refresh...")
                self.browser.driver.refresh()
                time.sleep(2)

            # Prüfe erneut
            return self.is_healthy()

        except Exception as e:
            logger.error(f"Auto-heal failed: {e}")
            return False


class CrossPlatformUtils:
    """Cross-platform Utility-Funktionen."""

    @staticmethod
    def take_full_page_screenshot(driver: webdriver.Chrome, filename: str) -> bool:
        """
        Erstellt Screenshot der gesamten Seite (cross-platform).

        Args:
            driver: WebDriver-Instanz
            filename: Dateiname für Screenshot

        Returns:
            True bei Erfolg
        """
        try:
            # Hole ursprüngliche Fenstergröße
            original_size = driver.get_window_size()

            # Ermittle Seitengröße
            page_height = driver.execute_script(
                "return Math.max(document.body.scrollHeight, "
                "document.body.offsetHeight, "
                "document.documentElement.clientHeight, "
                "document.documentElement.scrollHeight, "
                "document.documentElement.offsetHeight);"
            )

            # Setze Fenstergröße auf Seitengröße
            driver.set_window_size(original_size["width"], page_height)

            # Screenshot erstellen
            success = driver.save_screenshot(filename)

            # Ursprüngliche Größe wiederherstellen
            driver.set_window_size(original_size["width"], original_size["height"])

            return success

        except Exception as e:
            logger.error(f"Full page screenshot failed: {e}")
            return False

    @staticmethod
    def clear_browser_data(driver: webdriver.Chrome) -> bool:
        """
        Löscht Browser-Daten (cross-platform).

        Args:
            driver: WebDriver-Instanz

        Returns:
            True bei Erfolg
        """
        try:
            # Local Storage löschen
            driver.execute_script("localStorage.clear();")

            # Session Storage löschen
            driver.execute_script("sessionStorage.clear();")

            # Cookies löschen
            driver.delete_all_cookies()

            logger.info("Browser data cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to clear browser data: {e}")
            return False

    @staticmethod
    def inject_custom_css(driver: webdriver.Chrome, css: str) -> bool:
        """
        Injiziert Custom CSS in die Seite.

        Args:
            driver: WebDriver-Instanz
            css: CSS-Code

        Returns:
            True bei Erfolg
        """
        try:
            script = f"""
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
            """

            driver.execute_script(script)
            return True

        except Exception as e:
            logger.error(f"Failed to inject CSS: {e}")
            return False
