"""Element interaction utilities for browser automation."""

import logging
from typing import Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


class ElementInteractions:
    """Handles all element interactions like clicking, typing, waiting."""

    def __init__(self, driver: webdriver.Chrome, default_timeout: int = 10) -> None:
        """
        Initialize element interactions.

        Args:
            driver: WebDriver instance
            default_timeout: Default timeout for element operations
        """
        self.driver = driver
        self.default_timeout = default_timeout

    def safe_click(self, by: str, value: str, timeout: Optional[int] = None) -> bool:
        """
        Safe click with timeout handling.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            True on success, False on timeout
        """
        timeout = timeout or self.default_timeout
        try:
            self._wait_and_click((by, value), timeout)
            return True
        except TimeoutException:
            logger.warning(f"Timeout clicking element: {by}={value}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False

    def click_by_id(self, element_id: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by ID.

        Args:
            element_id: Element ID
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.ID, element_id), timeout)

    def click_by_css(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by CSS selector.

        Args:
            selector: CSS selector
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.CSS_SELECTOR, selector), timeout)

    def click_by_xpath(self, xpath: str, timeout: Optional[int] = None) -> WebElement:
        """
        Click element by XPath.

        Args:
            xpath: XPath expression
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        timeout = timeout or self.default_timeout
        return self._wait_and_click((By.XPATH, xpath), timeout)

    def send_keys_by_name(self, name: str, keys: str, timeout: Optional[int] = None) -> WebElement:
        """
        Send keys to element by name.

        Args:
            name: Name attribute
            keys: Keys to send
            timeout: Timeout in seconds

        Returns:
            The element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.NAME, name))
        )
        element.clear()  # Clear existing content
        element.send_keys(keys)
        logger.debug(f"Sent keys to element {name}: {keys}")
        return element

    def send_keys_by_id(self, element_id: str, keys: str, timeout: Optional[int] = None) -> WebElement:
        """
        Send keys to element by ID.

        Args:
            element_id: Element ID
            keys: Keys to send
            timeout: Timeout in seconds

        Returns:
            The element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.ID, element_id))
        )
        element.clear()
        element.send_keys(keys)
        logger.debug(f"Sent keys to element {element_id}: {keys}")
        return element

    def wait_for_element(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be present.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The found element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.presence_of_element_located((by, value))
        )
        logger.debug(f"Found element: {by}={value}")
        return element

    def wait_for_element_clickable(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be clickable.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The clickable element
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((by, value))
        )
        logger.debug(f"Element is clickable: {by}={value}")
        return element

    def _wait_and_click(self, locator: Tuple[str, str], timeout: int) -> WebElement:
        """
        Wait for element and click it.

        Args:
            locator: Tuple of strategy and value
            timeout: Timeout in seconds

        Returns:
            The clicked element
        """
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable(locator)
        )
        element.click()
        logger.debug(f"Clicked element: {locator}")
        return element

    def get_element_text(self, by: str, value: str, timeout: Optional[int] = None) -> str:
        """
        Get text content of an element.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            Element text content
        """
        timeout = timeout or self.default_timeout
        element = self.wait_for_element(by, value, timeout)
        text = element.text
        logger.debug(f"Got element text: {text}")
        return text

    def is_element_present(self, by: str, value: str) -> bool:
        """
        Check if element is present (without waiting).

        Args:
            by: Locator strategy
            value: Locator value

        Returns:
            True if element is present
        """
        try:
            self.driver.find_element(by, value)
            return True
        except Exception as e:
            logger.debug(f"Element not found: {by}={value}, error: {e}")
            return False
