#!/usr/bin/env python
"""
Advanced Scraping Example für Quick Browser Framework - GEFIXT
==============================================================

Zeigt erweiterte Funktionen wie Warten, Screenshots, Custom Options.
"""

import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from quick_browser import BrowserConfig, BrowserFramework


def main():
    """Erweiterte Web-Scraping Beispiele."""

    print("🚀 Quick Browser Framework - Advanced Example")
    print("=" * 55)

    # Custom Browser Configuration
    config = BrowserConfig(
        headless=False,  # Browser sichtbar für Demo
        kiosk=False,  # Windowed statt Kiosk
        show_console=True,  # Download-Progress anzeigen
        element_timeout=30,
        page_load_timeout=30,
        log_system_info=True  # Platform-Info loggen
    )

    # Browser Framework mit Custom Config
    with BrowserFramework(config) as browser:
        try:
            print("📝 Browser mit Custom Config gestartet...")
            driver = browser.driver
            wait = WebDriverWait(driver, 10)

            # Beispiel 1: Wikipedia Scraping
            print("\n📚 Beispiel 1: Wikipedia Scraping")
            print("-" * 35)

            driver.get("https://en.wikipedia.org/wiki/Python_(programming_language)")

            # Warten bis Seite geladen
            wait.until(EC.presence_of_element_located((By.ID, "firstHeading")))

            # Daten extrahieren
            title = driver.find_element(By.ID, "firstHeading").text
            print(f"📄 Titel: {title}")

            # Inhaltsverzeichnis extrahieren
            try:
                toc_elements = driver.find_elements(By.CSS_SELECTOR, "#toc .toctext")
                print(f"📋 Inhaltsverzeichnis ({len(toc_elements)} Punkte):")
                for i, element in enumerate(toc_elements[:5], 1):
                    print(f"   {i}. {element.text}")
            except Exception as e:
                print(f"❌ Fehler beim Extrahieren des Inhaltsverzeichnisses: {e}")

            # Screenshot
            driver.save_screenshot("wikipedia_python.png")
            print("📸 Screenshot: wikipedia_python.png")

            # Beispiel 2: News Scraping mit Scroll
            print("\n📰 Beispiel 2: News Headlines")
            print("-" * 30)

            driver.get("https://news.ycombinator.com")

            # Warten auf Headlines
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "titleline")))

            # Headlines sammeln
            headlines = []
            headline_elements = driver.find_elements(By.CSS_SELECTOR, ".titleline > a")

            for element in headline_elements[:10]:
                headlines.append({
                    "title": element.text,
                    "url": element.get_attribute("href")
                })

            print(f"📊 Gefunden: {len(headlines)} Headlines")
            for i, headline in enumerate(headlines[:5], 1):
                print(f"   {i}. {headline['title'][:60]}...")

            # Als JSON speichern
            with open("headlines.json", "w", encoding="utf-8") as f:
                json.dump(headlines, f, indent=2, ensure_ascii=False)
            print("💾 Headlines gespeichert: headlines.json")

            # Beispiel 3: Form Automation mit Helper-Methoden
            print("\n📝 Beispiel 3: Form Automation")
            print("-" * 32)

            driver.get("https://httpbin.org/forms/post")

            # Warten auf Form
            wait.until(EC.presence_of_element_located((By.NAME, "custname")))

            # ✅ Framework Helper-Methoden verwenden (gefixt!)
            print("🔧 Verwende Framework Helper-Methoden...")
            browser.send_keys_by_name("custname", "Test User")
            browser.send_keys_by_name("custtel", "123-456-7890")
            browser.send_keys_by_name("custemail", "test@example.com")
            browser.send_keys_by_name("comments", "Automatisiert mit Quick Browser Framework!")

            print("✅ Formular mit Helper-Methoden ausgefüllt")
            print("   (Submit wird übersprungen - nur Demo)")

            # Beispiel 4: JavaScript Execution
            print("\n⚙️ Beispiel 4: JavaScript Execution")
            print("-" * 35)

            # Custom JavaScript ausführen
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    screenResolution: screen.width + 'x' + screen.height,
                    timestamp: new Date().toISOString()
                };
            """)

            print("🔧 JavaScript Ergebnisse:")
            for key, value in page_info.items():
                if key == "userAgent":
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")

            # Beispiel 5: Performance Metrics (vereinfacht)
            print("\n📊 Beispiel 5: Performance Metrics")
            print("-" * 37)

            # Performance mit einfachem JavaScript
            performance = driver.execute_script("""
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

            print("⏱️ Performance Daten:")
            for metric, value in performance.items():
                print(f"   {metric}: {value}ms")

            # Beispiel 6: Framework Utilities verwenden (verfügbare!)
            print("\n🛠️ Beispiel 6: Framework Utilities")
            print("-" * 35)

            # ✅ Verfügbare Framework-Methoden verwenden
            try:
                # Scroll-Utility verwenden
                browser.scroll_to_element("body")
                print("✅ Scroll-Utility verwendet")

                # Element entfernen (falls vorhanden)
                browser.remove_elements_by_ids(("some-nonexistent-id",))
                print("✅ Element-Removal getestet")

                # Safe click testen
                if browser.safe_click("tag name", "body", timeout=2):
                    print("✅ Safe-Click funktioniert")
                else:
                    print("⚠️ Safe-Click Timeout (normal für body)")

            except Exception as e:
                print(f"⚠️ Framework Utilities Fehler: {e}")

            # ✅ Utils importieren die tatsächlich existieren
            try:
                from quick_browser import ElementWaiter, PerformanceMonitor

                # Performance Monitor testen
                perf_monitor = PerformanceMonitor(driver)
                load_time = perf_monitor.get_page_load_time()
                memory_info = perf_monitor.get_memory_usage()

                print("🔍 Framework Performance Monitor:")
                print(f"   Ladezeit: {load_time:.2f}s")
                if memory_info and memory_info.get('used_heap'):
                    print(f"   Memory: {memory_info['used_heap'] / 1024 / 1024:.1f}MB")

                # Element Waiter testen
                waiter = ElementWaiter(driver, default_timeout=5)
                print(f"✅ ElementWaiter bereit (Timeout: {waiter.default_timeout}s)")

            except ImportError as e:
                print(f"⚠️ Einige Utils nicht verfügbar: {e}")
            except Exception as e:
                print(f"⚠️ Utils-Test Fehler: {e}")

        except Exception as e:
            print(f"❌ Fehler: {e}")
            import traceback
            traceback.print_exc()

    print("✅ Advanced Example abgeschlossen!")
    print("\n💡 Erstellte Dateien:")
    print("   - wikipedia_python.png")
    print("   - headlines.json")
    print("\n🎯 Framework Features demonstriert:")
    print("   ✅ Context Manager")
    print("   ✅ Custom Configuration")
    print("   ✅ Helper-Methoden")
    print("   ✅ Performance Monitoring")
    print("   ✅ Element Utilities")


if __name__ == "__main__":
    main()
