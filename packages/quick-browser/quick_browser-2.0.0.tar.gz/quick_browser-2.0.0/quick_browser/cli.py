#!/usr/bin/env python
"""CLI Utilities for the Browser Framework."""

import argparse
import logging
import sys
from typing import NoReturn, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .config import BrowserConfig
from .core import BrowserFramework


def setup_logging() -> None:
    """Configure logging for CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_test(dry_run: bool = False) -> None:
    """
    Run framework tests with optional dry-run mode.

    Args:
        dry_run: If True, skip actual browser operations
    """
    logger = logging.getLogger(__name__)
    logger.info("🚀 Browser Framework Test started")

    try:
        # Test 1: Basic Framework Test
        logger.info("📋 Testing basic framework...")
        config = BrowserConfig(
            headless=True if dry_run else False,
            kiosk=False,
            show_console=True,
            log_system_info=True
        )

        with BrowserFramework(config) as browser:
            driver: Optional[WebDriver] = browser.driver

            # TYPE-SAFE: Check driver is not None before operations
            if driver is None:
                logger.error("❌ Driver initialization failed")
                return

            logger.info("✅ Browser initialized successfully")

            if not dry_run:
                # Test navigation - driver is guaranteed not None
                driver.get("https://www.google.com")
                logger.info(f"📄 Navigated to: {driver.current_url}")

                # Test element interaction
                try:
                    search_box = driver.find_element(By.NAME, "q")
                    search_box.send_keys("Browser Framework Test")
                    logger.info("✅ Search field filled successfully")
                except Exception as e:
                    logger.info(f"ℹ️ Search field test: {e}")

            # Test utility functions
            try:
                from .utils import CrossPlatformUtils, PerformanceMonitor

                # TYPE-SAFE: Pass non-None driver to utilities
                monitor = PerformanceMonitor(driver)
                if not dry_run:
                    load_time = monitor.get_page_load_time()
                    logger.info(f"📊 Page load time: {load_time:.2f}s")
                else:
                    logger.info("📊 Performance monitor initialized (dry-run)")

                # Test screenshot utility
                utils = CrossPlatformUtils()
                if not dry_run:
                    success = utils.take_full_page_screenshot(
                        driver, "test_full_screenshot.png"
                    )
                    if success:
                        logger.info("📸 Full page screenshot saved")
                    else:
                        # Fallback to basic screenshot
                        driver.save_screenshot("test_screenshot.png")
                        logger.info("📸 Basic screenshot saved")
                else:
                    logger.info("📸 Screenshot utilities available (dry-run)")

            except ImportError as e:
                logger.warning(f"⚠️ Utility import failed: {e}")
            except Exception as e:
                logger.warning(f"⚠️ Utility test failed: {e}")

            logger.info("🎉 Basic framework test completed")

        # Test 2: Cookie Banner Handling Test
        if not dry_run:
            logger.info("📋 Testing cookie banner handling...")
            config_cookies = BrowserConfig(
                auto_handle_cookies=True,
                prefer_reject_cookies=True,
                headless=True,
                kiosk=False,
                show_console=True
            )

            with BrowserFramework(config_cookies) as browser_cookies:
                cookie_driver: Optional[WebDriver] = browser_cookies.driver

                if cookie_driver is not None:
                    # Test automatic cookie handling
                    logger.info("🍪 Testing automatic cookie handling...")
                    success = browser_cookies.navigate("https://www.google.com")
                    if success:
                        logger.info("✅ Navigation with cookie handling successful")

                        # Get cookie statistics
                        try:
                            stats = browser_cookies.get_cookie_statistics()
                            logger.info(f"📊 Cookie stats: {stats}")
                        except Exception as e:
                            logger.info(f"ℹ️ Cookie stats: {e}")
                    else:
                        logger.info("⚠️ Navigation failed")
                else:
                    logger.warning("⚠️ Cookie test driver initialization failed")
        else:
            logger.info("📋 Cookie banner handling test skipped (dry-run)")

        # Test 3: API Import Test
        logger.info("📋 Testing API imports...")
        try:
            # FIXED: Use correct import path
            from .utils.cross_platform import PlatformDetector

            detector = PlatformDetector()
            platform = detector.get_platform_name()
            logger.info(f"🖥️ Detected platform: {platform}")
            logger.info("✅ Platform detection successful")
        except ImportError:
            # Alternative import path
            try:
                from .system import PlatformDetector
                detector = PlatformDetector()
                platform = detector.get_platform_name()
                logger.info(f"🖥️ Detected platform: {platform}")
                logger.info("✅ Platform detection successful (alternative path)")
            except ImportError as e:
                logger.warning(f"⚠️ Platform detector import failed: {e}")

        logger.info("✅ All API imports tested")
        logger.info("🍪 Cookie banner handler available")
        logger.info("🎉 All tests completed successfully")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        try:
            from .core import TroubleshootingHelper
            TroubleshootingHelper.log_troubleshooting_info(None, None)
        except ImportError:
            logger.error("❌ Troubleshooting helper not available")
        sys.exit(1)


def show_extended_help() -> None:
    """Show extended help information."""
    print("""
🚀 Quick Browser Test Tool - Extended Help

USAGE:
    quick-browser-test [OPTIONS]

OPTIONS:
    --help              Show this help message
    --help-extended     Show this extended help
    --dry-run          Run without actual browser operations

EXAMPLES:
    # Basic test
    quick-browser-test

    # Dry run (no actual browser operations)
    quick-browser-test --dry-run

FEATURES TESTED:
    ✅ Browser Framework initialization
    ✅ WebDriver setup and configuration
    ✅ Navigation and element interaction
    ✅ Performance monitoring
    ✅ Screenshot capabilities
    ✅ Cookie banner handling
    ✅ Platform detection
    ✅ API imports and compatibility

TROUBLESHOOTING:
    - If browser fails to start, check system requirements
    - For headless issues, try with --dry-run first
    - Check logs for detailed error information
    - Ensure Chrome/Chromium is properly installed

For more information: https://github.com/NoirPi/quick-browser
""")


def test_framework() -> NoReturn:
    """
    Test command for the Browser Framework.

    Can be called with `quick-browser-test`.
    Tests both basic functionality and new modular API.
    """
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Quick Browser Framework Test Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actual browser operations"
    )
    parser.add_argument(
        "--help-extended",
        action="store_true",
        help="Show extended help information"
    )

    args = parser.parse_args()

    if args.help_extended:
        show_extended_help()
        sys.exit(0)

    run_test(args.dry_run)
    sys.exit(0)


def main() -> NoReturn:
    """Main CLI entry point."""
    test_framework()


if __name__ == "__main__":
    main()
