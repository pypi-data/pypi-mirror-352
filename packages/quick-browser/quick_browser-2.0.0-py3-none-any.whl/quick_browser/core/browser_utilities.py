"""Browser utility functions and helper methods."""

import logging
from typing import Tuple

from selenium import webdriver

logger = logging.getLogger(__name__)


class BrowserUtilities:
    """Utility methods for browser manipulation and interaction."""

    def __init__(self, driver: webdriver.Chrome) -> None:
        """
        Initialize browser utilities.

        Args:
            driver: WebDriver instance
        """
        self.driver = driver

    def remove_elements_by_ids(self, element_ids: Tuple[str, ...]) -> None:
        """
        Remove multiple elements by ID.

        Args:
            element_ids: Tuple of element IDs to remove
        """
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
        Scroll to an element.

        Args:
            selector: CSS selector of the element
            behavior: Scroll behavior ('smooth' or 'instant')
        """
        scroll_script = f"""
        const element = document.querySelector(arguments[0]);
        if (element) {{
            element.scrollIntoView({{ behavior: '{behavior}', block: 'center' }});
        }}
        """
        try:
            self.driver.execute_script(scroll_script, selector)
            logger.debug(f"Scrolled to element: {selector}")
        except Exception as e:
            logger.warning(f"Failed to scroll to element {selector}: {e}")

    def take_screenshot(self, filename: str) -> bool:
        """
        Take a screenshot.

        Args:
            filename: Path to save screenshot

        Returns:
            True if successful
        """
        try:
            result = self.driver.save_screenshot(filename)
            if result:
                logger.info(f"Screenshot saved: {filename}")
            return result
        except Exception as e:
            logger.error(f"Failed to take screenshot {filename}: {e}")
            return False

    def execute_javascript(self, script: str, *args) -> any:
        """
        Execute JavaScript in the browser.

        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            Script execution result
        """
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug(f"Executed JavaScript: {script[:50]}...")
            return result
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            raise

    def get_page_source(self) -> str:
        """
        Get current page source.

        Returns:
            Page source HTML
        """
        try:
            source = self.driver.page_source
            logger.debug(f"Retrieved page source ({len(source)} characters)")
            return source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return ""

    def refresh_page(self) -> None:
        """Refresh the current page."""
        try:
            self.driver.refresh()
            logger.debug("Page refreshed")
        except Exception as e:
            logger.error(f"Failed to refresh page: {e}")

    def get_current_url(self) -> str:
        """
        Get current page URL.

        Returns:
            Current URL
        """
        try:
            url = self.driver.current_url
            logger.debug(f"Current URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return ""

    def navigate_to(self, url: str) -> None:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
        """
        try:
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise
