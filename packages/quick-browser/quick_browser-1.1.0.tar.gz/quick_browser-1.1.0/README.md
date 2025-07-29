# 🚀 Quick Browser Framework

> **Wiederverwendbares Browser Framework für Web-Automatisierung - 64-bit only**

Ein einfaches, aber mächtiges Python-Framework für Browser-Automatisierung basierend auf Selenium. Entwickelt für Windows 64-bit Systeme mit Fokus auf Einfachheit und Zuverlässigkeit.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2064--bit-lightgrey.svg)](https://www.microsoft.com/windows)

## ✨ Features

- 🔧 **Einfache API** - Minimaler Setup-Code für maximale Produktivität
- 🌐 **Multi-Browser Support** - Chrome, Firefox, Edge
- ⚡ **Performance Optimiert** - Schnelle Startzeiten und effiziente Ressourcennutzung
- 🛡️ **Robust** - Eingebaute Error-Handling und Retry-Mechanismen
- 🎯 **Windows Optimiert** - Speziell für Windows 64-bit entwickelt
- 📦 **Zero Config** - Funktioniert out-of-the-box ohne komplexe Konfiguration
- 🔄 **Auto-Update** - Automatische WebDriver-Updates
- 📸 **Screenshot Support** - Eingebaute Screenshot-Funktionalität

## 🚀 Quick Start

### Installation

```bash
# Aus Gitea Registry
pip install --index-url https://git.noircoding.de/api/packages/NoirPi/pypi/simple/ quick-browser

# Oder mit requirements.txt
echo "--extra-index-url https://git.noircoding.de/api/packages/NoirPi/pypi/simple/" >> requirements.txt
echo "quick-browser>=1.1.0" >> requirements.txt
pip install -r requirements.txt
```

### Basic Usage

```python
from browser_framework import BrowserManager

# Browser starten
browser_manager = BrowserManager()
driver = browser_manager.get_driver()

# Webseite öffnen
driver.get("https://www.google.com")

# Element finden und interagieren
search_box = driver.find_element("name", "q")
search_box.send_keys("Python automation")
search_box.submit()

# Screenshot erstellen
driver.save_screenshot("result.png")

# Cleanup
browser_manager.cleanup()
```

### Advanced Configuration

```python
from browser_framework import BrowserManager, BrowserConfig

# Custom Konfiguration
config = BrowserConfig(
    headless=True,
    window_size=(1920, 1080),
    user_agent="Custom User Agent",
    download_directory="./downloads",
    page_load_timeout=30
)

browser_manager = BrowserManager(config=config)
driver = browser_manager.get_driver()
```

## 📚 Examples

Das `examples/` Verzeichnis enthält vollständige Beispiele:

- **`basic_usage.py`** - Grundlegende Browser-Automatisierung
- **`advanced_scraping.py`** - Erweiterte Scraping-Techniken mit Custom Config

### Beispiele ausführen

```bash
# Basis Beispiel
python examples/basic_usage.py

# Erweiterte Beispiele
python examples/advanced_scraping.py
```

## 🛠️ API Reference

### BrowserManager

Hauptklasse für Browser-Management.

```python
browser_manager = BrowserManager(config=None, browser_type="chrome")
```

**Parameter:**
- `config` (BrowserConfig, optional): Custom Browser-Konfiguration
- `browser_type` (str): Browser-Typ ("chrome", "firefox", "edge")

**Methoden:**
- `get_driver()`: Startet Browser und gibt WebDriver zurück
- `cleanup()`: Schließt Browser und bereinigt Ressourcen

### BrowserConfig

Konfigurationsklasse für Browser-Einstellungen.

```python
config = BrowserConfig(
    headless=False,           # Headless-Modus
    window_size=(1366, 768),  # Fenstergröße
    user_agent=None,          # Custom User Agent
    download_directory=None,   # Download-Verzeichnis
    enable_javascript=True,   # JavaScript aktivieren
    load_images=True,         # Bilder laden
    page_load_timeout=30      # Timeout für Seitenladen
)
```

## 🔧 CLI Tools

Das Framework enthält praktische CLI-Tools:

```bash
# Framework testen
quick-browser-test

# Hilfe anzeigen
quick-browser-test --help
```

## 📋 Requirements

- **Python**: 3.8 oder höher
- **Betriebssystem**: Windows 64-bit
- **Browser**: Chrome, Firefox oder Edge
- **RAM**: Mindestens 4GB empfohlen

### Python Dependencies

```
selenium>=4.15.0
requests>=2.31.0
tqdm>=4.66.0
pywin32>=306
keyring>=24.0.0
```

## 🏗️ Development

### Setup Development Environment

```bash
# Repository klonen
git clone https://git.noircoding.de/NoirPi/quick-browser.git
cd quick-browser

# Virtual Environment erstellen
python -m venv .venv
.venv\Scripts\activate

# Development Dependencies installieren
pip install -e .[dev]
```

### Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=browser_framework

# Specific Test
pytest tests/test_browser_manager.py
```

### Code Quality

```bash
# Linting mit Ruff
ruff check .

# Auto-Fix
ruff check . --fix

# Type Checking
mypy browser_framework/
```

### Build Package

```bash
# Clean Build
python -m build

# Upload to Gitea
twine upload --repository gitea dist/*
```

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Changes (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

## 📝 Changelog

### v1.1.0 (2025-06-02)
- ✨ Initiale Release
- 🔧 Basic Browser Management
- 📦 Windows 64-bit Optimierung
- 🛡️ Error Handling
- 📸 Screenshot Support

## 📄 License

Dieses Projekt ist unter der MIT License lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🆘 Support

- **Issues**: [Gitea Issues](https://git.noircoding.de/NoirPi/quick-browser/issues)
- **Documentation**: [README](https://git.noircoding.de/NoirPi/quick-browser#readme)
- **Email**: noirpi@noircoding.de

## 🙏 Acknowledgments

- Selenium WebDriver Team
- Python Community
- Alle Beta-Tester und Contributors

---

**Made with ❤️ by NoirPi**

*Quick Browser Framework - Because browser automation shouldn't be complicated!*