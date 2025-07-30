#!/usr/bin/env python
"""
Basic Usage Example für Quick Browser Framework
===============================================

Minimales Beispiel für die grundlegende Verwendung des Browser-Frameworks.
"""

import time

from quick_browser import BrowserConfig, BrowserFramework, PlatformConfigFactory


def main_basic_automation() -> None:
    """Grundlegendes Browser-Automatisierung Beispiel."""

    print("🚀 Quick Browser Framework - Basic Example")
    print("=" * 45)

    # Platform-optimierte Konfiguration
    config = PlatformConfigFactory.create_auto_config(
        headless=False,
        show_console=True,
        element_timeout=15
    )

    # Context Manager für automatisches Cleanup
    with BrowserFramework(config) as browser:
        try:
            print("🌐 Navigiere zu Google...")
            if not browser.navigate("https://www.google.com"):
                print("❌ Navigation fehlgeschlagen")
                return

            print("🔍 Suche nach 'Python automation'...")
            search_element = browser.send_keys_by_name("q", "Python automation")
            if search_element:
                search_element.submit()
                print("✅ Suche gesendet")

                # Kurz warten für Ergebnisse
                time.sleep(3)

                # Suchergebnisse zählen
                results = browser.driver.find_elements("css selector", "h3")
                print(f"✅ Gefunden: {len(results)} Suchergebnisse")

                # Erste 3 Ergebnisse anzeigen
                for i, result in enumerate(results[:3], 1):
                    title = result.text.strip()
                    if title:
                        print(f"   {i}. {title}")
            else:
                print("❌ Suchfeld nicht gefunden")

            print("📸 Screenshot erstellen...")
            browser.driver.save_screenshot("search_results.png")
            print("   Screenshot gespeichert: search_results.png")

        except Exception as e:
            print(f"❌ Fehler: {e}")


def main_manual_management() -> None:
    """Beispiel mit manueller Browser-Verwaltung."""

    print("\n🔧 Quick Browser Framework - Manuelle Verwaltung")
    print("=" * 50)

    config = BrowserConfig(
        headless=False,
        show_console=True,
        element_timeout=10
    )

    browser = BrowserFramework(config)

    try:
        # Expliziter Setup
        browser.setup()

        print("🌐 Navigiere zu GitHub...")
        browser.driver.get("https://github.com")

        # Titel ausgeben
        title = browser.driver.title
        print(f"📄 Seitentitel: {title}")

        # Screenshot
        browser.driver.save_screenshot("github_page.png")
        print("📸 Screenshot gespeichert: github_page.png")

    except Exception as e:
        print(f"❌ Fehler: {e}")
    finally:
        # Expliziter Cleanup
        browser.quit()


def main() -> None:
    """Führe alle Beispiele aus."""

    try:
        # Beispiel 1: Context Manager (Empfohlen)
        main_basic_automation()

        # Beispiel 2: Manuelle Verwaltung
        main_manual_management()

        print("\n🎉 Alle Beispiele abgeschlossen!")
        print("\n💡 Erstellt Dateien:")
        print("   - search_results.png")
        print("   - github_page.png")

        print("\n🏆 Empfehlung:")
        print("   Verwende Context Manager für automatisches Cleanup")

    except KeyboardInterrupt:
        print("\n⏹️ Beispiele durch Benutzer unterbrochen")
    except Exception as e:
        print(f"\n❌ Beispiel fehlgeschlagen: {e}")


if __name__ == "__main__":
    main()
