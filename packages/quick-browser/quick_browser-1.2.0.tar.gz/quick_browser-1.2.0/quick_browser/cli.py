#!/usr/bin/env python
"""CLI Utilities für das Browser Framework."""

import logging
import sys
from typing import NoReturn

from .config import BrowserConfig
from .core import BrowserFramework


def setup_logging() -> None:
    """Konfiguriert Logging für CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def test_framework() -> NoReturn:
    """
    Test-Kommando für das Browser Framework.

    Kann mit `quick-browser-test` aufgerufen werden.
    """
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Browser Framework Test gestartet")

    try:
        config = BrowserConfig(
            headless=False, kiosk=False, show_console=True, log_system_info=True
        )

        with BrowserFramework(config) as browser:
            logger.info("✅ Browser erfolgreich initialisiert")

            # Test-Navigation
            browser.driver.get("https://www.google.com")
            logger.info(f"📄 Navigiert zu: {browser.driver.current_url}")

            # Test-Element-Interaktion
            search_box = browser.driver.find_element("name", "q")
            search_box.send_keys("Browser Framework Test")
            logger.info("✅ Suchfeld erfolgreich gefüllt")

            logger.info("🎉 Browser Framework Test erfolgreich abgeschlossen")
            browser.driver.save_screenshot("test_screenshot.png")

    except Exception as e:
        logger.error(f"❌ Test fehlgeschlagen: {e}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    test_framework()
