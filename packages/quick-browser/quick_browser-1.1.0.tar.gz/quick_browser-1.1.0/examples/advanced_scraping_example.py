#!/usr/bin/env python
"""
Advanced Scraping Example für Quick Browser Framework
====================================================

Zeigt erweiterte Funktionen wie Warten, Screenshots, Custom Options.
"""

import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from browser_framework import BrowserConfig, BrowserManager


def main():
    """Erweiterte Web-Scraping Beispiele."""

    print("🚀 Quick Browser Framework - Advanced Example")
    print("=" * 55)

    # Custom Browser Configuration
    config = BrowserConfig(
        headless=False,  # Browser sichtbar für Demo
        window_size=(1920, 1080),
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        download_directory="./downloads",
        enable_javascript=True,
        load_images=True,
        page_load_timeout=30
    )

    # Browser Manager mit Custom Config
    browser_manager = BrowserManager(config=config)

    try:
        print("📝 Starte Browser mit Custom Config...")
        driver = browser_manager.get_driver()
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
        except:
            print("   Kein Inhaltsverzeichnis gefunden")

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

        # Beispiel 3: Form Automation
        print("\n📝 Beispiel 3: Form Automation")
        print("-" * 32)

        driver.get("https://httpbin.org/forms/post")

        # Form ausfüllen
        wait.until(EC.presence_of_element_located((By.NAME, "custname")))

        driver.find_element(By.NAME, "custname").send_keys("Test User")
        driver.find_element(By.NAME, "custtel").send_keys("123-456-7890")
        driver.find_element(By.NAME, "custemail").send_keys("test@example.com")
        driver.find_element(By.NAME, "comments").send_keys("Automatisiert mit Quick Browser Framework!")

        print("✅ Formular ausgefüllt")
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

        # Performance Metrics
        print("\n📊 Beispiel 5: Performance Metrics")
        print("-" * 37)

        performance = driver.execute_script("""
            const perfData = performance.getEntriesByType('navigation')[0];
            return {
                loadTime: Math.round(perfData.loadEventEnd - perfData.navigationStart),
                domContentLoaded: Math.round(perfData.domContentLoadedEventEnd - perfData.navigationStart),
                responseTime: Math.round(perfData.responseEnd - perfData.requestStart)
            };
        """)

        print("⏱️ Performance Daten:")
        for metric, value in performance.items():
            print(f"   {metric}: {value}ms")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\n🔒 Browser schließen...")
        browser_manager.cleanup()

    print("✅ Advanced Example abgeschlossen!")
    print("\n💡 Erstelle Dateien:")
    print("   - wikipedia_python.png")
    print("   - headlines.json")


if __name__ == "__main__":
    main()
