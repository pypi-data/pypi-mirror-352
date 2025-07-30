#!/usr/bin/env python
"""Tests for Quick Browser Framework."""


import pytest

from quick_browser import BrowserConfig, BrowserFramework, __version__


class TestBrowserConfig:
    """Tests for BrowserConfig."""

    def test_config_creation(self) -> None:
        """Test that BrowserConfig can be created."""
        config = BrowserConfig()
        assert config is not None
        assert hasattr(config, "headless")
        assert hasattr(config, "download_timeout")

    def test_config_defaults(self) -> None:
        """Test default values of configuration."""
        config = BrowserConfig()
        assert config.headless is False
        assert config.kiosk is True
        assert config.download_timeout == 60
        assert config.element_timeout == 20
        assert config.page_load_timeout == 30

    def test_custom_config(self) -> None:
        """Test custom configuration."""
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

    def test_config_immutable(self) -> None:
        """Test that config objects are immutable (frozen dataclass)."""
        config = BrowserConfig()

        # Test that direct attribute assignment fails (frozen dataclass)
        with pytest.raises(AttributeError):
            config.headless = True

        # Verify config still has original values
        assert config.headless is False


class TestBrowserFramework:
    """Tests for BrowserFramework."""

    def test_browser_framework_import(self) -> None:
        """Test that BrowserFramework can be imported."""
        assert BrowserFramework is not None

    def test_browser_framework_creation(self) -> None:
        """Test that BrowserFramework can be created."""
        config = BrowserConfig()
        framework = BrowserFramework(config)

        assert framework is not None
        assert framework.config == config
        assert framework.driver is None  # Not yet initialized

    def test_context_manager_interface(self) -> None:
        """Test Context Manager Interface."""
        config = BrowserConfig(headless=True)
        framework = BrowserFramework(config)

        # Test __enter__ and __exit__ methods exist
        assert hasattr(framework, "__enter__")
        assert hasattr(framework, "__exit__")

    def test_helper_methods_exist(self) -> None:
        """Test that helper methods exist."""
        config = BrowserConfig()
        framework = BrowserFramework(config)

        # Test that helper methods are defined
        assert hasattr(framework, "safe_click")
        assert hasattr(framework, "click_by_id")
        assert hasattr(framework, "click_by_css")
        assert hasattr(framework, "send_keys_by_name")
        assert hasattr(framework, "scroll_to_element")
        assert hasattr(framework, "remove_elements_by_ids")


class TestImports:
    """Tests for imports and modules."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_main_imports(self) -> None:
        """Test that all main components can be imported."""
        from quick_browser import (
            AdvancedBrowserConfig,
            BrowserConfig,
            BrowserError,
            BrowserFramework,
            ChromiumManager,
            DownloadError,
            SetupError,
        )

        # Test that all imports are successful
        assert BrowserFramework is not None
        assert BrowserConfig is not None
        assert AdvancedBrowserConfig is not None
        assert ChromiumManager is not None
        assert BrowserError is not None
        assert SetupError is not None
        assert DownloadError is not None

    def test_utils_imports(self) -> None:
        """Test that utility classes can be imported."""
        from quick_browser import (
            BrowserHealthChecker,
            ElementWaiter,
            PerformanceMonitor,
        )

        assert ElementWaiter is not None
        assert PerformanceMonitor is not None
        assert BrowserHealthChecker is not None

    def test_backward_compatibility_alias(self) -> None:
        """Test that BrowserManager alias works."""
        from quick_browser import BrowserFramework, BrowserManager

        # BrowserManager should be identical to BrowserFramework
        assert BrowserManager is BrowserFramework


class TestConfiguration:
    """Tests for configuration and validation."""

    def test_advanced_config(self) -> None:
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

    def test_performance_flags_exist(self) -> None:
        """Test that performance flags are defined."""
        config = BrowserConfig()

        assert hasattr(config, "performance_flags")
        assert isinstance(config.performance_flags, list)
        assert len(config.performance_flags) > 0
        assert "--disable-extensions" in config.performance_flags

    def test_browser_prefs_exist(self) -> None:
        """Test that browser preferences are defined."""
        config = BrowserConfig()

        assert hasattr(config, "browser_prefs")
        assert isinstance(config.browser_prefs, dict)
        assert len(config.browser_prefs) > 0


class TestCrossPlatform:
    """Tests for cross-platform functionality."""

    def test_platform_detection(self) -> None:
        """Test platform detection."""
        from quick_browser.system import get_platform_info, is_linux, is_windows

        # At least one platform should be True
        platforms = [is_windows(), is_linux()]
        assert any(platforms)

        # Platform info should be available
        platform_info = get_platform_info()
        assert isinstance(platform_info, dict)
        assert 'system' in platform_info
        assert 'is_windows' in platform_info
        assert 'is_linux' in platform_info


# Simple function tests (not class-based)
def test_simple_config_creation() -> None:
    """Simple test for config creation."""
    config = BrowserConfig()
    assert config.headless is False
    assert config.download_timeout == 60


def test_simple_framework_creation() -> None:
    """Simple test for framework creation."""
    config = BrowserConfig()
    framework = BrowserFramework(config)
    assert framework is not None


def test_simple_version_check() -> None:
    """Simple version check."""
    assert __version__ is not None
    assert "." in __version__  # Version should contain dot


def test_simple_import_check() -> None:
    """Simple import check."""
    from quick_browser import BrowserConfig, BrowserFramework
    assert BrowserFramework is not None
    assert BrowserConfig is not None


if __name__ == "__main__":
    # Run standard tests
    pytest.main([__file__, "-v"])
