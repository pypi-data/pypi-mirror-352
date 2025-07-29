#!/usr/bin/env python
"""
Basic Usage Example für Quick Browser Framework
===============================================

Zeigt die grundlegende Verwendung des Browser Frameworks.
"""

import time

from browser_framework import BrowserManager


def main():
    """Grundlegendes Beispiel für Browser-Automatisierung."""

    print("🚀 Quick Browser Framework - Basic Example")
    print("=" * 50)

    # Browser Manager erstellen
    browser_manager = BrowserManager()

    try:
        print("📝 Starte Browser...")
        driver = browser_manager.get_driver()

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

    finally:
        print("🔒 Browser schließen...")
        browser_manager.cleanup()

    print("✅ Beispiel abgeschlossen!")


if __name__ == "__main__":
    main()
