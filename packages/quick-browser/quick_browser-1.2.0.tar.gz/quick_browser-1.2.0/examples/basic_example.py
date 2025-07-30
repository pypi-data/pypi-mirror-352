#!/usr/bin/env python
"""
Basic Usage Example für Quick Browser Framework - GEFIXT
========================================================

Zeigt die grundlegende Verwendung des Browser Frameworks.
"""
import time

from quick_browser import BrowserConfig, BrowserFramework


def main():
    """Grundlegendes Beispiel für Browser-Automatisierung."""

    print("🚀 Quick Browser Framework - Basic Example")
    print("=" * 50)

    config = BrowserConfig()

    # Browser Framework mit Context Manager (RICHTIG!)
    with BrowserFramework(config) as browser:
        try:
            print("📝 Browser gestartet...")
            driver = browser.driver  # ✅ .driver statt .get_driver()

            print("🌐 Navigiere zu Google...")
            driver.get("https://www.google.com")

            print("🔍 Suche nach 'Python automation'...")
            search_box = driver.find_element("name", "q")
            search_box.send_keys("Python automation")
            search_box.submit()

            print("⏳ Warte auf Ergebnisse...")
            time.sleep(3)

            # Ergebnisse anzeigen
            results = driver.find_elements("css selector", "h3")
            print(f"✅ Gefunden: {len(results)} Suchergebnisse")

            for i, result in enumerate(results[:5], 1):
                print(f"   {i}. {result.text}")

            print("📸 Screenshot erstellen...")
            driver.save_screenshot("google_search_results.png")
            print("   Screenshot gespeichert: google_search_results.png")

        except Exception as e:
            print(f"❌ Fehler: {e}")

    # ✅ Context Manager macht automatisch cleanup!
    print("✅ Beispiel abgeschlossen!")


if __name__ == "__main__":
    main()
