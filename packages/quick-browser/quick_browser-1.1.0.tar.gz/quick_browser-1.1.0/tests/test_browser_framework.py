#!/usr/bin/env python
"""Tests für Browser Framework."""

import pytest

from browser_framework import BrowserConfig, BrowserFramework


def test_config_creation():
    """Test dass BrowserConfig erstellt werden kann."""
    config = BrowserConfig()
    assert config is not None
    assert hasattr(config, "headless")
    assert hasattr(config, "download_timeout")


def test_browser_framework_import():
    """Test dass BrowserFramework importiert werden kann."""
    assert BrowserFramework is not None


def test_version_import():
    """Test dass Version importiert werden kann."""
    try:
        from browser_framework._version import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
    except ImportError:
        # Version-Modul noch nicht verfügbar
        pass


def test_custom_config():
    """Test benutzerdefinierte Konfiguration."""
    config = BrowserConfig(headless=True, download_timeout=120)
    assert config.headless is True
    assert config.download_timeout == 120


# Weitere Tests können hier hinzugefügt werden
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
