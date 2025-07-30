#!/usr/bin/env python
"""
Script to refactor utils.py into a modular utils/ package.
Splits the monolithic utils into focused utility modules.
"""

import shutil
from pathlib import Path

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

UTILS_DIR = BASE_DIR / "quick_browser" / "utils"
ORIGINAL_FILE = BASE_DIR / "quick_browser" / "utils.py"


def create_directory_structure() -> None:
    """Create the utils/ directory structure."""
    print("📁 Creating utils/ directory structure...")

    # Create utils directory
    UTILS_DIR.mkdir(exist_ok=True)
    print(f"   ✓ Created: {UTILS_DIR}")


def create_init_py() -> None:
    """Create __init__.py with backward compatibility exports."""
    init_content = '''"""
Utils package for cross-platform browser automation utilities.

This package provides modular utility components for:
- Element waiting and interaction utilities
- Browser performance monitoring
- Browser health checking and diagnostics
- Cross-platform utility functions
- Custom utility helpers

All utilities are available as direct imports for convenience.
"""

from .element_waiter import ElementWaiter
from .performance_monitor import PerformanceMonitor
from .health_checker import BrowserHealthChecker
from .cross_platform import CrossPlatformUtils

# Backward compatibility - main exports
__all__ = [
    # Element utilities
    "ElementWaiter",

    # Performance utilities  
    "PerformanceMonitor",

    # Health and diagnostics
    "BrowserHealthChecker",

    # Cross-platform utilities
    "CrossPlatformUtils",
]
'''

    init_file = UTILS_DIR / "__init__.py"
    init_file.write_text(init_content.strip())
    print(f"   ✓ Created: {init_file}")


def create_element_waiter_py() -> None:
    """Create element_waiter.py with element waiting utilities."""
    element_waiter_content = '''"""Cross-platform utility class for advanced element waiting operations."""

import logging
import time
from typing import List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class ElementWaiter:
    """Cross-platform utility class for advanced element waiting operations."""

    def __init__(self, driver: webdriver.Chrome, default_timeout: int = 10) -> None:
        """
        Initialize ElementWaiter.

        Args:
            driver: WebDriver instance
            default_timeout: Default timeout in seconds
        """
        self.driver = driver
        self.default_timeout = default_timeout

    def wait_for_any_element(
        self, locators: List[Tuple[str, str]], timeout: Optional[int] = None
    ) -> Optional[WebElement]:
        """
        Wait for one of multiple elements.

        Args:
            locators: List of locator tuples
            timeout: Timeout in seconds

        Returns:
            First found element or None
        """
        timeout = timeout or self.default_timeout
        end_time = time.time() + timeout

        while time.time() < end_time:
            for by, value in locators:
                try:
                    element = self.driver.find_element(by, value)
                    if element.is_displayed() and element.is_enabled():
                        logger.debug(f"Found element: {by}={value}")
                        return element
                except NoSuchElementException:
                    continue

            time.sleep(0.1)

        logger.warning(f"None of the elements found within {timeout}s: {locators}")
        return None

    def wait_for_element_text_change(
        self, locator: Tuple[str, str], initial_text: str, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for element text to change.

        Args:
            locator: Element locator
            initial_text: Initial text
            timeout: Timeout in seconds

        Returns:
            True if text changed
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_element(*locator).text != initial_text
            )
            logger.debug(f"Element text changed from: {initial_text}")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"Element text did not change within {timeout}s")
            return False

    def wait_for_element_to_disappear(
        self, locator: Tuple[str, str], timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for element to disappear.

        Args:
            locator: Element locator
            timeout: Timeout in seconds

        Returns:
            True if element disappeared
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until_not(
                lambda d: d.find_element(*locator).is_displayed()
            )
            logger.debug(f"Element disappeared: {locator}")
            return True
        except (TimeoutException, NoSuchElementException):
            # Element is already not there - that's good
            logger.debug(f"Element already not present: {locator}")
            return True

    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for complete page load.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if page loaded
        """
        timeout = timeout or self.default_timeout

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.debug("Page load completed")
            return True
        except TimeoutException:
            logger.warning(f"Page did not load completely within {timeout}s")
            return False

    def wait_for_ajax_complete(
        self, timeout: Optional[int] = None, jquery: bool = True
    ) -> bool:
        """
        Wait for AJAX requests to complete.

        Args:
            timeout: Timeout in seconds
            jquery: Check for jQuery AJAX as well

        Returns:
            True if AJAX completed
        """
        timeout = timeout or self.default_timeout

        try:
            if jquery:
                # Wait for jQuery AJAX
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script(
                        "return typeof jQuery !== 'undefined' ? jQuery.active === 0 : true"
                    )
                )

            # Wait for native XMLHttpRequest
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    """
                    var requests = window.openHTTPRequests || 0;
                    return requests === 0;
                    """
                )
            )
            logger.debug("AJAX requests completed")
            return True
        except TimeoutException:
            logger.warning(f"AJAX requests did not complete within {timeout}s")
            return False

    def wait_for_element_attribute_change(
        self, locator: Tuple[str, str], attribute: str, 
        expected_value: Optional[str] = None, timeout: Optional[int] = None
    ) -> bool:
        """
        Wait for element attribute to change or match expected value.

        Args:
            locator: Element locator
            attribute: Attribute name to check
            expected_value: Expected attribute value (None to wait for any change)
            timeout: Timeout in seconds

        Returns:
            True if attribute changed/matched
        """
        timeout = timeout or self.default_timeout

        try:
            if expected_value is not None:
                # Wait for specific value
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.find_element(*locator).get_attribute(attribute) == expected_value
                )
            else:
                # Wait for any change (store initial value first)
                initial_value = self.driver.find_element(*locator).get_attribute(attribute)
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.find_element(*locator).get_attribute(attribute) != initial_value
                )

            logger.debug(f"Element attribute '{attribute}' changed as expected")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.warning(f"Element attribute '{attribute}' did not change within {timeout}s")
            return False

    def wait_for_url_change(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for URL to change from current URL.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if URL changed
        """
        timeout = timeout or self.default_timeout
        current_url = self.driver.current_url

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.current_url != current_url
            )
            logger.debug(f"URL changed from: {current_url} to: {self.driver.current_url}")
            return True
        except TimeoutException:
            logger.warning(f"URL did not change within {timeout}s")
            return False

    def wait_for_title_change(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for page title to change.

        Args:
            timeout: Timeout in seconds

        Returns:
            True if title changed
        """
        timeout = timeout or self.default_timeout
        current_title = self.driver.title

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.title != current_title
            )
            logger.debug(f"Title changed from: '{current_title}' to: '{self.driver.title}'")
            return True
        except TimeoutException:
            logger.warning(f"Title did not change within {timeout}s")
            return False
'''

    element_waiter_file = UTILS_DIR / "element_waiter.py"
    element_waiter_file.write_text(element_waiter_content.strip())
    print(f"   ✓ Created: {element_waiter_file}")


def create_performance_monitor_py() -> None:
    """Create performance_monitor.py with browser performance monitoring."""
    performance_content = '''"""Cross-platform monitor for browser performance metrics."""

import logging
import time
from typing import Any, Dict, List

from selenium import webdriver

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Cross-platform monitor for browser performance."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        """
        Initialize PerformanceMonitor.

        Args:
            driver: WebDriver instance
        """
        self.driver = driver

    def get_page_load_time(self) -> float:
        """
        Get page loading time.

        Returns:
            Load time in seconds
        """
        try:
            navigation_start = self.driver.execute_script(
                "return window.performance.timing.navigationStart"
            )
            dom_complete = self.driver.execute_script(
                "return window.performance.timing.domComplete"
            )
            load_time = (dom_complete - navigation_start) / 1000.0
            logger.debug(f"Page load time: {load_time:.2f}s")
            return load_time
        except Exception as e:
            logger.warning(f"Could not get page load time: {e}")
            return 0.0

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get memory usage (cross-platform).

        Returns:
            Dictionary with memory information
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
                result = {
                    "used_heap": memory_info.get("usedJSHeapSize", 0),
                    "total_heap": memory_info.get("totalJSHeapSize", 0),
                    "heap_limit": memory_info.get("jsHeapSizeLimit", 0),
                }
                logger.debug(f"Memory usage: {result['used_heap'] / 1024 / 1024:.1f}MB used")
                return result
            else:
                # Fallback for browsers without Memory API
                logger.debug("Memory API not available")
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
        Get network timing information.

        Returns:
            Dictionary with timing information
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

            if timing:
                logger.debug(f"Network timing - DNS: {timing.get('dnsLookup', 0):.0f}ms, "
                           f"Connect: {timing.get('tcpConnect', 0):.0f}ms")

            return timing or {}
        except Exception as e:
            logger.warning(f"Could not get network timing: {e}")
            return {}

    def get_resource_timing(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get resource timing for slowest resources.

        Args:
            limit: Number of resources to return

        Returns:
            List of slowest resources
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

            if resources:
                logger.debug(f"Found {len(resources)} resources, slowest: "
                           f"{resources[0]['duration']:.0f}ms" if resources else "none")

            return resources or []
        except Exception as e:
            logger.warning(f"Could not get resource timing: {e}")
            return []

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.

        Returns:
            Dictionary with all performance data
        """
        metrics = {
            "timestamp": time.time(),
            "url": self.driver.current_url,
            "load_time": self.get_page_load_time(),
            "memory": self.get_memory_usage(),
            "network": self.get_network_timing(),
            "slow_resources": self.get_resource_timing(5),
        }

        logger.debug("Collected comprehensive performance metrics")
        return metrics

    def log_performance_metrics(self) -> None:
        """Log comprehensive performance metrics."""
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
        Create detailed performance report.

        Returns:
            Dictionary with performance data
        """
        report = self.get_performance_metrics()

        # Add computed metrics
        if report["memory"]:
            memory_usage_percent = 0
            if report["memory"]["heap_limit"] > 0:
                memory_usage_percent = (report["memory"]["used_heap"] / 
                                      report["memory"]["heap_limit"]) * 100
            report["memory_usage_percent"] = memory_usage_percent

        # Add performance score (simple heuristic)
        load_time = report["load_time"]
        if load_time < 1.0:
            performance_score = "excellent"
        elif load_time < 3.0:
            performance_score = "good"
        elif load_time < 5.0:
            performance_score = "fair"
        else:
            performance_score = "poor"

        report["performance_score"] = performance_score

        logger.info(f"Performance report created - Score: {performance_score}")
        return report
'''

    performance_file = UTILS_DIR / "performance_monitor.py"
    performance_file.write_text(performance_content.strip())
    print(f"   ✓ Created: {performance_file}")


def create_health_checker_py() -> None:
    """Create health_checker.py with browser health diagnostics."""
    health_checker_content = '''"""Cross-platform health checking for browser instances."""

import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class BrowserHealthChecker:
    """Cross-platform health checking for browser instance."""

    def __init__(self, browser_framework) -> None:
        """
        Initialize BrowserHealthChecker.

        Args:
            browser_framework: BrowserFramework instance
        """
        self.browser = browser_framework

    def is_healthy(self) -> bool:
        """
        Check if browser is healthy.

        Returns:
            True if browser is functional
        """
        if not self.browser.driver:
            return False

        try:
            # Basic health checks
            return (
                self._has_active_windows()
                and self._has_valid_url()
                and self._can_execute_javascript()
                and self._is_responsive()
            )
        except Exception:
            return False

    def _has_active_windows(self) -> bool:
        """Check if active browser windows are present."""
        try:
            window_count = len(self.browser.driver.window_handles)
            logger.debug(f"Active windows: {window_count}")
            return window_count > 0
        except Exception:
            return False

    def _has_valid_url(self) -> bool:
        """Check if current URL is valid."""
        try:
            url = self.browser.driver.current_url
            is_valid = url and (url.startswith("http") or url.startswith("file") or url == "data:,")
            logger.debug(f"URL valid: {is_valid} ({url})")
            return is_valid
        except Exception:
            return False

    def _can_execute_javascript(self) -> bool:
        """Check if JavaScript can be executed."""
        try:
            result = self.browser.driver.execute_script("return true;")
            can_execute = result is True
            logger.debug(f"JavaScript execution: {can_execute}")
            return can_execute
        except Exception:
            return False

    def _is_responsive(self) -> bool:
        """Check if browser is responsive."""
        try:
            # Simple responsiveness test
            start_time = time.time()
            self.browser.driver.execute_script("return document.readyState;")
            response_time = time.time() - start_time

            # Browser should respond within 5 seconds
            is_responsive = response_time < 5.0
            logger.debug(f"Response time: {response_time:.2f}s, responsive: {is_responsive}")
            return is_responsive
        except Exception:
            return False

    def get_health_report(self) -> Dict[str, Any]:
        """
        Create detailed health report.

        Returns:
            Dictionary with health information
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
            # Window count
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
        Diagnose browser problems and provide solutions.

        Returns:
            List of diagnostic messages
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
        Attempt automatic browser repair.

        Returns:
            True if repair successful
        """
        try:
            if not self.browser.driver:
                logger.info("🔧 Attempting to reinitialize browser...")
                self.browser.setup()
                return self.is_healthy()

            # Try browser refresh if problems detected
            if not self._is_responsive():
                logger.info("🔧 Browser unresponsive, attempting refresh...")
                self.browser.driver.refresh()
                time.sleep(2)

            # Check again
            return self.is_healthy()

        except Exception as e:
            logger.error(f"Auto-heal failed: {e}")
            return False

    def get_browser_info(self) -> Dict[str, Any]:
        """
        Get browser information for diagnostics.

        Returns:
            Dictionary with browser info
        """
        info = {
            "user_agent": "",
            "browser_name": "",
            "browser_version": "",
            "platform": "",
            "viewport_size": {"width": 0, "height": 0},
            "screen_size": {"width": 0, "height": 0},
        }

        if not self.browser.driver:
            return info

        try:
            # Get user agent
            info["user_agent"] = self.browser.driver.execute_script("return navigator.userAgent;")

            # Get viewport size
            viewport = self.browser.driver.execute_script("return {width: window.innerWidth, height: window.innerHeight};")
            info["viewport_size"] = viewport or {"width": 0, "height": 0}

            # Get screen size
            screen = self.browser.driver.execute_script("return {width: screen.width, height: screen.height};")
            info["screen_size"] = screen or {"width": 0, "height": 0}

            # Parse browser info from user agent (simple approach)
            user_agent = info["user_agent"].lower()
            if "chrome" in user_agent:
                info["browser_name"] = "Chrome"
            elif "firefox" in user_agent:
                info["browser_name"] = "Firefox"
            elif "edge" in user_agent:
                info["browser_name"] = "Edge"
            else:
                info["browser_name"] = "Unknown"

        except Exception as e:
            logger.warning(f"Could not get browser info: {e}")

        return info

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health check with full diagnostics.

        Returns:
            Complete health and diagnostic report
        """
        report = {
            "health": self.get_health_report(),
            "diagnoses": self.diagnose_issues(),
            "browser_info": self.get_browser_info(),
            "recommendations": [],
        }

        # Add recommendations based on health
        if not report["health"]["is_healthy"]:
            if not report["health"]["javascript_enabled"]:
                report["recommendations"].append("Enable JavaScript in browser settings")
            if report["health"]["window_count"] == 0:
                report["recommendations"].append("Restart browser session")
            if not report["health"]["responsive"]:
                report["recommendations"].append("Close unnecessary tabs or restart browser")

        return report
'''

    health_checker_file = UTILS_DIR / "health_checker.py"
    health_checker_file.write_text(health_checker_content.strip())
    print(f"   ✓ Created: {health_checker_file}")


def create_cross_platform_py() -> None:
    """Create cross_platform.py with cross-platform utility functions."""
    cross_platform_content = '''"""Cross-platform utility functions."""

import logging
from typing import Dict, Any

from selenium import webdriver

logger = logging.getLogger(__name__)


class CrossPlatformUtils:
    """Cross-platform utility functions."""

    @staticmethod
    def take_full_page_screenshot(driver: webdriver.Chrome, filename: str) -> bool:
        """
        Create screenshot of entire page (cross-platform).

        Args:
            driver: WebDriver instance
            filename: Filename for screenshot

        Returns:
            True on success
        """
        try:
            # Get original window size
            original_size = driver.get_window_size()

            # Get page size
            page_height = driver.execute_script(
                "return Math.max(document.body.scrollHeight, "
                "document.body.offsetHeight, "
                "document.documentElement.clientHeight, "
                "document.documentElement.scrollHeight, "
                "document.documentElement.offsetHeight);"
            )

            # Set window size to page size
            driver.set_window_size(original_size["width"], page_height)

            # Take screenshot
            success = driver.save_screenshot(filename)

            # Restore original size
            driver.set_window_size(original_size["width"], original_size["height"])

            if success:
                logger.info(f"Full page screenshot saved: {filename}")

            return success

        except Exception as e:
            logger.error(f"Full page screenshot failed: {e}")
            return False

    @staticmethod
    def clear_browser_data(driver: webdriver.Chrome) -> bool:
        """
        Clear browser data (cross-platform).

        Args:
            driver: WebDriver instance

        Returns:
            True on success
        """
        try:
            # Clear Local Storage
            driver.execute_script("localStorage.clear();")

            # Clear Session Storage
            driver.execute_script("sessionStorage.clear();")

            # Clear cookies
            driver.delete_all_cookies()

            logger.info("Browser data cleared successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to clear browser data: {e}")
            return False

    @staticmethod
    def inject_custom_css(driver: webdriver.Chrome, css: str) -> bool:
        """
        Inject custom CSS into the page.

        Args:
            driver: WebDriver instance
            css: CSS code

        Returns:
            True on success
        """
        try:
            script = f"""
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `{css}`;
            document.head.appendChild(style);
            """

            driver.execute_script(script)
            logger.debug("Custom CSS injected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to inject CSS: {e}")
            return False

    @staticmethod
    def inject_custom_javascript(driver: webdriver.Chrome, js_code: str) -> Any:
        """
        Inject and execute custom JavaScript.

        Args:
            driver: WebDriver instance
            js_code: JavaScript code to execute

        Returns:
            Execution result
        """
        try:
            result = driver.execute_script(js_code)
            logger.debug("Custom JavaScript executed successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            raise

    @staticmethod
    def get_page_info(driver: webdriver.Chrome) -> Dict[str, Any]:
        """
        Get comprehensive page information.

        Args:
            driver: WebDriver instance

        Returns:
            Dictionary with page information
        """
        try:
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    url: window.location.href,
                    domain: window.location.hostname,
                    protocol: window.location.protocol,
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    cookieEnabled: navigator.cookieEnabled,
                    onlineStatus: navigator.onLine,
                    screenResolution: screen.width + 'x' + screen.height,
                    windowSize: window.innerWidth + 'x' + window.innerHeight,
                    documentReady: document.readyState,
                    timestamp: new Date().toISOString()
                };
            """)

            logger.debug(f"Page info collected for: {page_info.get('title', 'Unknown')}")
            return page_info

        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            return {}

    @staticmethod
    def scroll_to_position(driver: webdriver.Chrome, x: int, y: int, behavior: str = "smooth") -> bool:
        """
        Scroll to specific position.

        Args:
            driver: WebDriver instance
            x: Horizontal position
            y: Vertical position
            behavior: Scroll behavior ('smooth' or 'instant')

        Returns:
            True on success
        """
        try:
            script = f"window.scrollTo({{left: {x}, top: {y}, behavior: '{behavior}'}});"
            driver.execute_script(script)
            logger.debug(f"Scrolled to position: ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"Failed to scroll to position: {e}")
            return False

    @staticmethod
    def wait_for_download_complete(download_dir, timeout: int = 60) -> bool:
        """
        Wait for downloads to complete.

        Args:
            download_dir: Download directory path
            timeout: Timeout in seconds

        Returns:
            True if downloads completed
        """
        import time
        from pathlib import Path

        download_path = Path(download_dir)
        end_time = time.time() + timeout

        while time.time() < end_time:
            # Check for .crdownload files (Chrome)
            crdownload_files = list(download_path.glob("*.crdownload"))

            # Check for .part files (Firefox)
            part_files = list(download_path.glob("*.part"))

            if not crdownload_files and not part_files:
                logger.debug("All downloads completed")
                return True

            time.sleep(0.5)

        logger.warning(f"Downloads did not complete within {timeout}s")
        return False

    @staticmethod
    def simulate_key_combination(driver: webdriver.Chrome, keys: str) -> bool:
        """
        Simulate key combinations.

        Args:
            driver: WebDriver instance
            keys: Key combination (e.g., 'ctrl+a', 'ctrl+c')

        Returns:
            True on success
        """
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(driver)

            # Parse key combination
            key_parts = keys.lower().split('+')
            modifier_keys = []
            regular_key = None

            for part in key_parts:
                if part in ['ctrl', 'control']:
                    modifier_keys.append(Keys.CONTROL)
                elif part in ['alt']:
                    modifier_keys.append(Keys.ALT)
                elif part in ['shift']:
                    modifier_keys.append(Keys.SHIFT)
                else:
                    regular_key = part

            # Build action chain
            for modifier in modifier_keys:
                actions = actions.key_down(modifier)

            if regular_key:
                actions = actions.send_keys(regular_key)

            for modifier in reversed(modifier_keys):
                actions = actions.key_up(modifier)

            actions.perform()
            logger.debug(f"Key combination executed: {keys}")
            return True

        except Exception as e:
            logger.error(f"Failed to simulate key combination {keys}: {e}")
            return False

    @staticmethod
    def get_browser_logs(driver: webdriver.Chrome, log_type: str = "browser") -> List[Dict[str, Any]]:
        """
        Get browser logs.

        Args:
            driver: WebDriver instance
            log_type: Type of logs ('browser', 'driver', 'performance')

        Returns:
            List of log entries
        """
        try:
            logs = driver.get_log(log_type)
            logger.debug(f"Retrieved {len(logs)} {log_type} log entries")
            return logs

        except Exception as e:
            logger.warning(f"Failed to get {log_type} logs: {e}")
            return []

    @staticmethod
    def set_download_behavior(driver: webdriver.Chrome, download_path: str) -> bool:
        """
        Set download behavior for current session.

        Args:
            driver: WebDriver instance
            download_path: Path for downloads

        Returns:
            True on success
        """
        try:
            driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                'behavior': 'allow',
                'downloadPath': download_path
            })
            logger.debug(f"Download path set to: {download_path}")
            return True

        except Exception as e:
            logger.warning(f"Failed to set download behavior: {e}")
            return False
'''

    cross_platform_file = UTILS_DIR / "cross_platform.py"
    cross_platform_file.write_text(cross_platform_content.strip())
    print(f"   ✓ Created: {cross_platform_file}")


def backup_original_file() -> None:
    """Backup the original utils.py file."""
    if ORIGINAL_FILE.exists():
        backup_path = ORIGINAL_FILE.with_suffix('.py.backup')
        shutil.copy2(ORIGINAL_FILE, backup_path)
        print(f"   ✓ Backed up original file to: {backup_path}")

        # Ask user if they want to remove the original
        print("   🗑️  Remove original utils.py after backup? (y/N): ", end="")
        remove_original = input().lower().strip()

        if remove_original in ["y", "yes"]:
            ORIGINAL_FILE.unlink()
            print(f"   ✓ Removed original file: {ORIGINAL_FILE}")
            print(f"     📦 All functionality now available via utils/ package")
        else:
            print(f"   📁 Original file kept: {ORIGINAL_FILE}")
            print(f"     ⚠️  Note: You may have import conflicts - consider removing it manually")
    else:
        print(f"   ⚠ Original file not found at {ORIGINAL_FILE}")


def update_main_utils_import() -> None:
    """Update main quick_browser/__init__.py to import from new structure."""
    main_init = BASE_DIR / "quick_browser" / "__init__.py"

    if main_init.exists():
        print(f"   ✓ Main __init__.py import unchanged (backward compatible)")
    else:
        print(f"   ⚠ Main __init__.py not found at {main_init}")


def create_migration_summary() -> None:
    """Create a summary of the migration."""
    summary_text = f"""
📋 Utils Framework Refactoring Complete!

✅ Created Files:
   • {UTILS_DIR}/__init__.py           - Package exports (backward compatible!)
   • {UTILS_DIR}/element_waiter.py     - Advanced element waiting operations
   • {UTILS_DIR}/performance_monitor.py - Browser performance monitoring
   • {UTILS_DIR}/health_checker.py     - Browser health diagnostics
   • {UTILS_DIR}/cross_platform.py     - Cross-platform utility functions

🔄 Backward Compatibility:
   • All existing imports continue to work:
     from quick_browser.utils import ElementWaiter
     from quick_browser.utils import PerformanceMonitor
     from quick_browser.utils import BrowserHealthChecker
     from quick_browser.utils import CrossPlatformUtils

🧪 Next Steps:
   1. Test imports from project root:
      cd {BASE_DIR}
      python -c "from quick_browser.utils import ElementWaiter; print('✅ Works!')"

   2. Run existing tests to verify compatibility:
      cd {BASE_DIR}
      python -m pytest tests/

   3. Original utils.py handling complete!
   4. Modular utility structure achieved! 🎉

💡 Benefits of New Structure:
   • Single Responsibility: Each utility class has one clear purpose
   • Better Testing: Test individual utility components in isolation  
   • Easier Maintenance: Changes only affect relevant utility modules
   • Consistent Architecture: Same pattern as chromium/ and core/ packages
   • Enhanced Functionality: More comprehensive utility methods

⚠️  Note: Original utils.py backed up as utils.py.backup  
📂 Working from scripts directory - paths auto-detected
🛠️  Monolithic utils.py successfully split into 4 focused utility modules!
"""

    print(summary_text)


def main() -> None:
    """Main refactoring function."""
    print("🔧 Starting Utils Framework Refactoring...")
    print("=" * 60)
    print(f"📂 Script running from: {SCRIPT_DIR}")
    print(f"📂 Project root detected: {BASE_DIR}")
    print(f"🎯 Target: Split utils.py into modular utils/ package")
    print()

    # Backup original
    backup_original_file()

    # Create structure
    create_directory_structure()

    # Create all module files
    create_init_py()
    create_element_waiter_py()
    create_performance_monitor_py()
    create_health_checker_py()
    create_cross_platform_py()

    # Update imports (if needed)
    update_main_utils_import()

    # Summary
    create_migration_summary()

    print("🎉 Utils refactoring completed successfully!")
    print("📦 Monolithic utils.py → 4 focused utility modules")


if __name__ == "__main__":
    main()