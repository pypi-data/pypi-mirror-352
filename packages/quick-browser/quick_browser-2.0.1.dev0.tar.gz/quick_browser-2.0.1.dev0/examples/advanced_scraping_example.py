#!/usr/bin/env python
"""
Advanced Scraping Example for Quick Browser Framework - FIXED
==============================================================

Shows advanced features like waiting, screenshots, custom options.
"""

import json
from typing import Any, Dict, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as expected_condition
from selenium.webdriver.support.ui import WebDriverWait

from quick_browser import BrowserConfig, BrowserFramework


def main() -> None:
    """Advanced web scraping examples."""

    print("🚀 Quick Browser Framework - Advanced Example")
    print("=" * 55)

    # Custom Browser Configuration
    config = BrowserConfig(
        headless=False,  # Browser visible for demo
        kiosk=False,  # Windowed instead of kiosk
        show_console=True,  # Show download progress
        element_timeout=30,
        page_load_timeout=30,
        log_system_info=True  # Log platform info
    )

    # Browser Framework with Custom Config
    with BrowserFramework(config) as browser:
        try:
            print("📝 Browser started with custom config...")
            driver: Optional[WebDriver] = browser.driver

            # TYPE-SAFE: Check driver is not None
            if driver is None:
                print("❌ Driver initialization failed")
                return

            # Now driver is guaranteed to be non-None for MyPy
            wait = WebDriverWait(driver, 10)

            # Example 1: Wikipedia Scraping
            print("\n📚 Example 1: Wikipedia Scraping")
            print("-" * 35)

            driver.get("https://en.wikipedia.org/wiki/Python_(programming_language)")

            # Wait until page loaded
            wait.until(expected_condition.presence_of_element_located((By.ID, "firstHeading")))

            # Extract data
            title_element = driver.find_element(By.ID, "firstHeading")
            title = title_element.text
            print(f"📄 Title: {title}")

            # Extract table of contents
            try:
                toc_elements = driver.find_elements(By.CSS_SELECTOR, "#toc .toctext")
                print(f"📋 Table of Contents ({len(toc_elements)} items):")
                for i, element in enumerate(toc_elements[:5], 1):
                    print(f"   {i}. {element.text}")
            except Exception as e:
                print(f"❌ Error extracting table of contents: {e}")

            # Screenshot
            driver.save_screenshot("wikipedia_python.png")
            print("📸 Screenshot: wikipedia_python.png")

            # Example 2: News Scraping with Scroll
            print("\n📰 Example 2: News Headlines")
            print("-" * 30)

            driver.get("https://news.ycombinator.com")

            # Wait for headlines
            wait.until(expected_condition.presence_of_element_located((By.CLASS_NAME, "titleline")))

            # Collect headlines
            headlines: List[Dict[str, Optional[str]]] = []
            headline_elements = driver.find_elements(By.CSS_SELECTOR, ".titleline > a")

            for element in headline_elements[:10]:
                href = element.get_attribute("href")
                headlines.append({
                    "title": element.text,
                    "url": href
                })

            print(f"📊 Found: {len(headlines)} Headlines")
            for i, headline in enumerate(headlines[:5], 1):
                title_text = headline.get("title", "")
                if title_text:
                    print(f"   {i}. {title_text[:60]}...")

            # Save as JSON
            with open("headlines.json", "w", encoding="utf-8") as f:
                json.dump(headlines, f, indent=2, ensure_ascii=False)
            print("💾 Headlines saved: headlines.json")

            # Example 3: Form Automation with Helper Methods
            print("\n📝 Example 3: Form Automation")
            print("-" * 32)

            driver.get("https://httpbin.org/forms/post")

            # Wait for form
            wait.until(expected_condition.presence_of_element_located((By.NAME, "custname")))

            # ✅ Use Framework Helper Methods (fixed!)
            print("🔧 Using framework helper methods...")
            browser.send_keys_by_name("custname", "Test User")
            browser.send_keys_by_name("custtel", "123-456-7890")
            browser.send_keys_by_name("custemail", "test@example.com")
            browser.send_keys_by_name("comments", "Automated with Quick Browser Framework!")

            print("✅ Form filled using helper methods")
            print("   (Submit skipped - demo only)")

            # Example 4: JavaScript Execution
            print("\n⚙️ Example 4: JavaScript Execution")
            print("-" * 35)

            # Execute custom JavaScript
            page_info_result = driver.execute_script("""
                return {
                    title: document.title,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    screenResolution: screen.width + 'x' + screen.height,
                    timestamp: new Date().toISOString()
                };
            """)

            # TYPE-SAFE: Handle potential None result
            if page_info_result and isinstance(page_info_result, dict):
                page_info: Dict[str, Any] = page_info_result
                print("🔧 JavaScript Results:")
                for key, value in page_info.items():
                    if key == "userAgent" and isinstance(value, str):
                        print(f"   {key}: {value[:50]}...")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("⚠️ JavaScript execution returned unexpected result")

            # Example 5: Performance Metrics (simplified)
            print("\n📊 Example 5: Performance Metrics")
            print("-" * 37)

            # Performance with simple JavaScript
            performance_result = driver.execute_script("""
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    return {
                        loadTime: Math.round(perfData.loadEventEnd - perfData.navigationStart),
                        domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.navigationStart),
                        responseTime: Math.round(perfData.responseEnd - perfData.requestStart)
                    };
                }
                return { loadTime: 0, domContentLoaded: 0, responseTime: 0 };
            """)

            # TYPE-SAFE: Handle performance result
            if performance_result and isinstance(performance_result, dict):
                performance: Dict[str, Any] = performance_result
                print("⏱️ Performance Data:")
                for metric, value in performance.items():
                    print(f"   {metric}: {value}ms")
            else:
                print("⚠️ Performance data not available")

            # Example 6: Use Framework Utilities (available ones!)
            print("\n🛠️ Example 6: Framework Utilities")
            print("-" * 35)

            # ✅ Use available Framework methods
            try:
                # Use scroll utility
                browser.scroll_to_element("body")
                print("✅ Scroll utility used")

                # Element removal (if exists)
                browser.remove_elements_by_ids(("some-nonexistent-id",))
                print("✅ Element removal tested")

                # Test safe click
                if browser.safe_click("tag name", "body", timeout=2):
                    print("✅ Safe-click works")
                else:
                    print("⚠️ Safe-click timeout (normal for body)")

            except Exception as e:
                print(f"⚠️ Framework utilities error: {e}")

            # ✅ Import utils that actually exist
            from quick_browser import ElementWaiter, PerformanceMonitor
            try:

                # Test performance monitor - driver is guaranteed non-None
                perf_monitor = PerformanceMonitor(driver)
                load_time = perf_monitor.get_page_load_time()
                memory_info = perf_monitor.get_memory_usage()

                print("🔍 Framework Performance Monitor:")
                print(f"   Load time: {load_time:.2f}s")
                if memory_info and isinstance(memory_info, dict):
                    used_heap = memory_info.get('used_heap')
                    if isinstance(used_heap, (int, float)) and used_heap > 0:
                        print(f"   Memory: {used_heap / 1024 / 1024:.1f}MB")

                # Test element waiter - driver is guaranteed non-None
                waiter = ElementWaiter(driver, default_timeout=5)
                print(f"✅ ElementWaiter ready (Timeout: {waiter.default_timeout}s)")

            except ImportError as e:
                print(f"⚠️ Some utils not available: {e}")
            except Exception as e:
                print(f"⚠️ Utils test error: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("✅ Advanced example completed!")
    print("\n💡 Created files:")
    print("   - wikipedia_python.png")
    print("   - headlines.json")
    print("\n🎯 Framework features demonstrated:")
    print("   ✅ Context Manager")
    print("   ✅ Custom Configuration")
    print("   ✅ Helper Methods")
    print("   ✅ Performance Monitoring")
    print("   ✅ Element Utilities")


if __name__ == "__main__":
    main()
