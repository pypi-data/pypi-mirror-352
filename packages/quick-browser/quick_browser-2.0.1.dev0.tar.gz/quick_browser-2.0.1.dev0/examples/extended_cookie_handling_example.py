#!/usr/bin/env python
"""
Fixed Basic Usage Example - Compatible with existing CookieBannerConfig API
"""
import time
from typing import Optional

from quick_browser import (
    BrowserConfig,
    BrowserFramework,
    CookieBannerConfig,
    CookieBannerHandler,
    ElementWaiter,
    PlatformConfigFactory,
)


def create_compatible_cookie_config(
        prefer_reject: bool = True,
        verbose: bool = False,
        timeout: Optional[float] = None
) -> CookieBannerConfig:
    """
    Create compatible CookieBannerConfig with existing API.

    Args:
        prefer_reject: Whether to prefer reject buttons
        timeout: Timeout in seconds (compatible with framework)
        verbose: Enable verbose logging

    Returns:
        Compatible CookieBannerConfig instance
    """
    # Use only parameters that exist in current implementation
    return CookieBannerConfig(
        prefer_reject=prefer_reject,
        timeout_seconds=timeout,  # Reduced timeout for speed
        verbose=verbose
    )


def example_automatic_cookie_handling() -> None:
    """Example with automatic cookie banner handling."""
    print("🍪 Example 1: Automatic Cookie Banner Handling")
    print("=" * 50)

    # Create cookie-friendly config
    config = PlatformConfigFactory.create_cookie_friendly_config(
        headless=False,
        kiosk=False,
        show_console=True
    )

    with BrowserFramework(config) as browser:
        try:
            # Navigate with automatic cookie handling
            print("🌐 Navigating to Google (auto cookie handling)...")
            browser.navigate("https://www.google.com")

            print("🔍 Searching for 'Python automation'...")
            search_success = browser.send_keys_by_name("q", "Python automation", timeout=10)

            if search_success:
                search_success.submit()
                time.sleep(1)  # Reduced sleep for speed

                # Show results
                results = browser.driver.find_elements("css selector", "h3")
                print(f"✅ Found: {len(results)} search results")

                for i, result in enumerate(results[:3], 1):
                    title = result.text.strip()
                    if title:
                        print(f"   {i}. {title}")

            # Show cookie handling statistics
            stats = browser.get_cookie_statistics()
            print(f"\n📊 Cookie Statistics: {stats}")

        except Exception as e:
            print(f"❌ Error: {e}")


def example_manual_cookie_control() -> None:
    """Example with manual cookie banner control."""
    print("\n🍪 Example 2: Manual Cookie Banner Control")
    print("=" * 50)

    config = BrowserConfig(
        auto_handle_cookies=False,
        headless=False,
        kiosk=False,
        show_console=True
    )

    with BrowserFramework(config) as browser:
        try:
            print("🌐 Navigating to YouTube...")
            browser.driver.get("https://www.youtube.com")
            time.sleep(1)  # Reduced sleep

            # Manual cookie handling with preference
            if browser.handle_cookie_banner(prefer_reject=True):
                print("✅ Cookie banner handled successfully")
            else:
                print("ℹ️ No cookie banner found")

            print("🔍 Searching for content...")
            waiter = ElementWaiter(browser.driver, default_timeout=10)

            try:
                search_box = waiter.wait_for_element("name", "search_query", timeout=10)
                if search_box:
                    search_box.send_keys("Python tutorials")
                    search_box.submit()
                    time.sleep(1)  # Reduced sleep
                    print("✅ Search completed")
            except Exception as e:
                print(f"⚠️ Search failed: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")


def example_advanced_cookie_configuration() -> None:
    """Example with advanced cookie configuration."""
    print("\n🍪 Example 3: Advanced Cookie Configuration")
    print("=" * 50)

    # Compatible custom cookie banner configuration
    custom_config = create_compatible_cookie_config(
        prefer_reject=False,  # Accept cookies instead of rejecting
        timeout=5.0,  # Reduced timeout for speed
        verbose=True
    )

    config = BrowserConfig(
        auto_handle_cookies=False,
        headless=False,
        show_console=True
    )

    with BrowserFramework(config) as browser:
        try:
            print("🌐 Navigating to Facebook...")
            browser.driver.get("https://www.facebook.com")
            time.sleep(1)  # Reduced sleep

            print("🍪 Using custom cookie configuration...")
            custom_handler = CookieBannerHandler(browser.driver, custom_config)

            if custom_handler.handle_banner():
                print("✅ Cookie banner handled with custom config")
                stats = custom_handler.get_statistics()
                print(f"📊 Custom handler stats: {stats}")
            else:
                print("ℹ️ No cookie banner found")

        except Exception as e:
            print(f"❌ Error: {e}")


def example_multiple_sites() -> None:
    """Example testing multiple sites with cookie banners."""
    print("\n🍪 Example 4: Multiple Sites Cookie Handling")
    print("=" * 50)

    sites = [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.amazon.com",
        "https://www.linkedin.com"
    ]

    config = BrowserConfig(
        auto_handle_cookies=True,
        prefer_reject_cookies=True,
        headless=False,
        kiosk=False,
        show_console=True,
        element_timeout=10  # Reduced timeout for speed
    )

    with BrowserFramework(config) as browser:
        results = []

        for site in sites:
            try:
                print(f"🌐 Testing: {site}")
                browser.navigate(site)
                time.sleep(1)  # Reduced sleep time

                # Check if page loaded successfully
                current_url = browser.driver.current_url.lower()
                if "error" not in current_url and "chrome-error" not in current_url:
                    results.append(f"✅ {site} - Success")
                else:
                    results.append(f"⚠️ {site} - Page error")

            except Exception as e:
                results.append(f"❌ {site} - Error: {str(e)[:50]}...")

        print("\n📊 Results Summary:")
        for result in results:
            print(f"   {result}")

        # Overall statistics
        try:
            stats = browser.get_cookie_statistics()
            print("\n📈 Overall Cookie Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"⚠️ Could not retrieve statistics: {e}")


def main() -> None:
    """Run all cookie banner examples with proper error handling."""
    print("🚀 Quick Browser Framework - Cookie Banner Integration Examples")
    print("=" * 80)

    try:
        example_automatic_cookie_handling()
        time.sleep(1)

        example_manual_cookie_control()
        time.sleep(1)

        example_advanced_cookie_configuration()
        time.sleep(1)

        example_multiple_sites()

        print("\n🎉 All cookie banner examples completed!")

    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
