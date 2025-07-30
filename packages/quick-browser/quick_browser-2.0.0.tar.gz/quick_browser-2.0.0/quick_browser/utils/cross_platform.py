"""Cross-platform utility functions."""

import logging
from typing import Any, Dict, List

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
            from selenium.webdriver.common.action_chains import ActionChains
            from selenium.webdriver.common.keys import Keys

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
