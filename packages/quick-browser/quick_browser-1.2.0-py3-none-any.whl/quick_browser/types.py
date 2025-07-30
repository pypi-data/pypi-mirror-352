"""Type definitions und Protocols für das Browser Framework."""

from enum import Enum
from typing import Any, List, Protocol

from selenium.webdriver.common.by import By


class LocatorStrategy(Enum):
    """Selenium-Locator-Strategien."""

    ID = By.ID
    NAME = By.NAME
    CLASS_NAME = By.CLASS_NAME
    CSS_SELECTOR = By.CSS_SELECTOR
    XPATH = By.XPATH
    TAG_NAME = By.TAG_NAME
    LINK_TEXT = By.LINK_TEXT
    PARTIAL_LINK_TEXT = By.PARTIAL_LINK_TEXT


class WebDriverProtocol(Protocol):
    """Protocol für WebDriver-ähnliche Objekte."""

    def get(self, url: str) -> None: ...

    def quit(self) -> None: ...

    def execute_script(self, script: str, *args: Any) -> Any: ...

    def fullscreen_window(self) -> None: ...

    @property
    def window_handles(self) -> List[str]: ...
