"""Cross-platform health checking for browser instances."""

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
