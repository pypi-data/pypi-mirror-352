#!/usr/bin/env python
"""Tests für Quick Browser Framework."""


import pytest

from quick_browser import BrowserConfig, BrowserFramework, __version__


class TestBrowserConfig:
    """Tests für BrowserConfig."""

    def test_config_creation(self):
        """Test dass BrowserConfig erstellt werden kann."""
        config = BrowserConfig()
        assert config is not None
        assert hasattr(config, "headless")
        assert hasattr(config, "download_timeout")

    def test_config_defaults(self):
        """Test Standard-Werte der Konfiguration."""
        config = BrowserConfig()
        assert config.headless is False
        assert config.kiosk is True
        assert config.download_timeout == 60
        assert config.element_timeout == 20
        assert config.page_load_timeout == 30

    def test_custom_config(self):
        """Test benutzerdefinierte Konfiguration."""
        config = BrowserConfig(
            headless=True,
            download_timeout=120,
            element_timeout=30,
            kiosk=False
        )
        assert config.headless is True
        assert config.download_timeout == 120
        assert config.element_timeout == 30
        assert config.kiosk is False

    def test_config_immutable(self):
        """Test dass Config-Objekte unveränderlich sind (frozen dataclass)."""
        config = BrowserConfig()

        with pytest.raises(AttributeError):
            config.headless = True  # Sollte fehlschlagen da frozen=True


class TestBrowserFramework:
    """Tests für BrowserFramework."""

    def test_browser_framework_import(self):
        """Test dass BrowserFramework importiert werden kann."""
        assert BrowserFramework is not None

    def test_browser_framework_creation(self):
        """Test dass BrowserFramework erstellt werden kann."""
        config = BrowserConfig()
        framework = BrowserFramework(config)

        assert framework is not None
        assert framework.config == config
        assert framework.driver is None  # Noch nicht initialisiert

    def test_context_manager_interface(self):
        """Test Context Manager Interface."""
        config = BrowserConfig(headless=True)
        framework = BrowserFramework(config)

        # Test __enter__ und __exit__ Methoden existieren
        assert hasattr(framework, "__enter__")
        assert hasattr(framework, "__exit__")

    def test_helper_methods_exist(self):
        """Test dass Helper-Methoden existieren."""
        config = BrowserConfig()
        framework = BrowserFramework(config)

        # Test dass Helper-Methoden definiert sind
        assert hasattr(framework, "safe_click")
        assert hasattr(framework, "click_by_id")
        assert hasattr(framework, "click_by_css")
        assert hasattr(framework, "send_keys_by_name")
        assert hasattr(framework, "scroll_to_element")
        assert hasattr(framework, "remove_elements_by_ids")


class TestImports:
    """Tests für Imports und Module."""

    def test_version_import(self):
        """Test dass Version importiert werden kann."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_main_imports(self):
        """Test dass alle Haupt-Komponenten importiert werden können."""
        from quick_browser import (
            AdvancedBrowserConfig,
            BrowserConfig,
            BrowserError,
            BrowserFramework,
            ChromiumManager,
            DownloadError,
            SetupError,
        )

        # Test dass alle Imports erfolgreich sind
        assert BrowserFramework is not None
        assert BrowserConfig is not None
        assert AdvancedBrowserConfig is not None
        assert ChromiumManager is not None
        assert BrowserError is not None
        assert SetupError is not None
        assert DownloadError is not None

    def test_utils_imports(self):
        """Test dass Utility-Klassen importiert werden können."""
        from quick_browser import (
            BrowserHealthChecker,
            ElementWaiter,
            PerformanceMonitor,
        )

        assert ElementWaiter is not None
        assert PerformanceMonitor is not None
        assert BrowserHealthChecker is not None

    def test_backward_compatibility_alias(self):
        """Test dass BrowserManager Alias funktioniert."""
        from quick_browser import BrowserFramework, BrowserManager

        # BrowserManager sollte identisch mit BrowserFramework sein
        assert BrowserManager is BrowserFramework


class TestConfiguration:
    """Tests für Konfiguration und Validation."""

    def test_advanced_config(self):
        """Test AdvancedBrowserConfig."""
        from quick_browser import AdvancedBrowserConfig

        config = AdvancedBrowserConfig(
            headless=True,
            max_retries=5,
            window_size=(1920, 1080),
            user_agent="Custom Agent"
        )

        assert config.headless is True
        assert config.max_retries == 5
        assert config.window_size == (1920, 1080)
        assert config.user_agent == "Custom Agent"

    def test_performance_flags_exist(self):
        """Test dass Performance-Flags definiert sind."""
        config = BrowserConfig()

        assert hasattr(config, "performance_flags")
        assert isinstance(config.performance_flags, list)
        assert len(config.performance_flags) > 0
        assert "--disable-extensions" in config.performance_flags

    def test_browser_prefs_exist(self):
        """Test dass Browser-Präferenzen definiert sind."""
        config = BrowserConfig()

        assert hasattr(config, "browser_prefs")
        assert isinstance(config.browser_prefs, dict)
        assert len(config.browser_prefs) > 0


class TestCrossPlatform:
    """Tests für Cross-Platform Funktionalität."""

    def test_platform_detection(self):
        """Test Platform-Detection."""
        from quick_browser.system import get_platform_info, is_linux, is_windows

        # Mindestens eine Platform sollte True sein
        platforms = [is_windows(), is_linux()]
        assert any(platforms)

        # Platform-Info sollte verfügbar sein
        platform_info = get_platform_info()
        assert isinstance(platform_info, dict)
        assert 'system' in platform_info
        assert 'is_windows' in platform_info
        assert 'is_linux' in platform_info


# Einfache Funktions-Tests (keine Klassen-basiert)
def test_simple_config_creation():
    """Einfacher Test für Config-Erstellung."""
    config = BrowserConfig()
    assert config.headless is False
    assert config.download_timeout == 60


def test_simple_framework_creation():
    """Einfacher Test für Framework-Erstellung."""
    config = BrowserConfig()
    framework = BrowserFramework(config)
    assert framework is not None


def test_simple_version_check():
    """Einfacher Version-Check."""
    assert __version__ is not None
    assert "." in __version__  # Version sollte Punkt enthalten


def test_simple_import_check():
    """Einfacher Import-Check."""
    from quick_browser import BrowserConfig, BrowserFramework
    assert BrowserFramework is not None
    assert BrowserConfig is not None


if __name__ == "__main__":
    # Standard Tests ausführen
    pytest.main([__file__, "-v"])
