"""Cross-platform utility class for advanced element waiting operations."""

import logging
import time
from typing import List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
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

    def wait_for_element(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be present and visible.

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The found element

        Raises:
            TimeoutException: If element not found within timeout
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.visibility_of_element_located((by, value))
        )
        logger.debug(f"Found visible element: {by}={value}")
        return element

    def wait_for_element_present(self, by: str, value: str, timeout: Optional[int] = None) -> WebElement:
        """
        Wait for element to be present (not necessarily visible).

        Args:
            by: Locator strategy
            value: Locator value
            timeout: Timeout in seconds

        Returns:
            The found element

        Raises:
            TimeoutException: If element not found within timeout
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.presence_of_element_located((by, value))
        )
        logger.debug(f"Found present element: {by}={value}")
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

        Raises:
            TimeoutException: If element not clickable within timeout
        """
        timeout = timeout or self.default_timeout
        element = WebDriverWait(self.driver, timeout).until(
            expected_conditions.element_to_be_clickable((by, value))
        )
        logger.debug(f"Element is clickable: {by}={value}")
        return element

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
