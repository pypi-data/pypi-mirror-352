"""Cross-platform system utilities for Windows and Linux with robust console handling."""

import ctypes
import logging
import os
import platform
import sys
from contextlib import contextmanager
from typing import Dict, Generator

from tqdm.auto import tqdm

logger = logging.getLogger(__name__)


def is_windows() -> bool:
    """Check if Windows system."""
    return sys.platform == "win32"


def is_linux() -> bool:
    """Check if Linux system."""
    return sys.platform.startswith("linux")


def get_platform_info() -> Dict[str, any]:
    """
    Determine platform information.

    Returns:
        Dictionary with platform details
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'architecture': platform.architecture()[0],
        'is_windows': is_windows(),
        'is_linux': is_linux(),
        'is_64bit': platform.architecture()[0] == '64bit',
        'python_version': platform.python_version()
    }


def _safe_set_console_title_windows(title: str) -> bool:
    """
    Windows-specific console title setting.

    Args:
        title: Console title

    Returns:
        True on success, False on error
    """
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # Use SetConsoleTitleW for Unicode support
        result = kernel32.SetConsoleTitleW(title)
        return bool(result)
    except (OSError, ctypes.ArgumentError):
        # Fallback to ANSI version
        try:
            title_bytes = title.encode("cp1252", errors="replace")
            result = kernel32.SetConsoleTitleA(title_bytes)
            return bool(result)
        except Exception:
            return False


def _safe_set_console_title_linux(title: str) -> bool:
    """
    Linux-specific terminal title setting.

    Args:
        title: Terminal title

    Returns:
        True on success, False on error
    """
    try:
        # ANSI escape sequence for terminal title
        if os.environ.get('TERM'):
            sys.stdout.write(f'\033]0;{title}\007')
            sys.stdout.flush()
            return True
        return False
    except Exception:
        return False


def safe_set_console_title(title: str) -> bool:
    """
    Cross-platform console/terminal title setting.

    Args:
        title: Console/terminal title

    Returns:
        True on success, False on error
    """
    if is_windows():
        return _safe_set_console_title_windows(title)
    elif is_linux():
        return _safe_set_console_title_linux(title)
    else:
        # Other platforms - no title support
        return False


@contextmanager
def temp_console_windows(title: str = "Download Console") -> Generator[None, None, None]:
    """
    Windows-specific temporary console with robust error handling.

    Args:
        title: Console title

    Yields:
        None

    Note:
        This function will never raise exceptions - it gracefully degrades
        if console operations fail.
    """
    kernel32 = None
    console_window = 0
    console_allocated = False
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        # Check if console already exists
        console_window = kernel32.GetConsoleWindow()

        if console_window == 0:  # No console present
            try:
                if kernel32.AllocConsole():
                    console_allocated = True
                    logger.debug("✅ Console allocated successfully")
                    safe_set_console_title(title)
                else:
                    logger.debug("⚠️ AllocConsole failed, continuing without console")
                    # Don't raise error - just continue without console
                    yield
                    return
            except Exception as e:
                logger.debug(f"⚠️ Console allocation exception: {e}, continuing without console")
                yield
                return
        elif title:  # Console already exists, just set title
            safe_set_console_title(title)
            logger.debug("✅ Using existing console")

        # Try to open console streams
        try:
            sys.stdout = open(
                "CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace"
            )
            sys.stderr = open(
                "CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace"
            )
            logger.debug("✅ Console streams opened")
        except OSError as e:
            logger.debug(f"⚠️ Console streams not available: {e}, using fallback")
            # Fallback if console streams not available
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        yield

    except Exception as e:
        logger.debug(f"⚠️ Console setup error: {e}, continuing without console")
        yield
    finally:
        # Cleanup - always restore original streams
        try:
            if hasattr(sys.stdout, "close") and sys.stdout != old_stdout:
                try:
                    sys.stdout.close()
                except Exception:
                    pass
            if hasattr(sys.stderr, "close") and sys.stderr != old_stderr:
                try:
                    sys.stderr.close()
                except Exception:
                    pass

            sys.stdout = old_stdout
            sys.stderr = old_stderr

            # Only free console if we allocated it ourselves
            if console_allocated and kernel32:
                try:
                    kernel32.FreeConsole()
                    logger.debug("✅ Console freed")
                except Exception as e:
                    logger.debug(f"⚠️ Console free error: {e}")
        except Exception as e:
            logger.debug(f"⚠️ Console cleanup error: {e}")


@contextmanager
def temp_console_linux(title: str = "Download Terminal") -> Generator[None, None, None]:
    """
    Linux-specific temporary terminal configuration.

    Args:
        title: Terminal title

    Yields:
        None
    """
    # On Linux we use existing terminal
    original_title_set = safe_set_console_title(title)

    try:
        yield
    finally:
        # Reset terminal title is optional
        if original_title_set:
            safe_set_console_title("Terminal")


@contextmanager
def temp_console(title: str = "Download Console") -> Generator[None, None, None]:
    """
    Cross-platform temporary console/terminal - ROBUST VERSION.

    This function will NEVER raise exceptions. If console operations fail,
    it gracefully degrades and continues execution.

    Args:
        title: Console/terminal title

    Yields:
        None
    """
    try:
        if is_windows():
            with temp_console_windows(title):
                yield
        elif is_linux():
            with temp_console_linux(title):
                yield
        else:
            # Other platforms - just pass through
            yield
    except Exception as e:
        logger.debug(f"⚠️ Console context failed: {e}, continuing without console")
        # Always yield, even if console setup failed completely
        yield


@contextmanager
def safe_temp_console(title: str = "Download Console") -> Generator[None, None, None]:
    """
    Ultra-safe console context manager that will absolutely never fail.

    This is a bulletproof wrapper around temp_console that guarantees
    execution will continue even if all console operations fail.

    Args:
        title: Console/terminal title

    Yields:
        None
    """
    try:
        with temp_console(title):
            yield
    except Exception as e:
        logger.debug(f"⚠️ Even safe console failed: {e}, yielding anyway")
        # Absolutely guarantee we yield
        yield


def hide_console_if_needed(show_console: bool) -> None:
    """
    Cross-platform console hiding if desired.

    Args:
        show_console: True to keep console visible
    """
    if not show_console:
        if is_windows():
            try:
                ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 0
                )
            except Exception:
                pass  # Ignore errors when hiding
        elif is_linux():
            # On Linux we cannot hide the terminal
            # This is also not common - Linux users expect a terminal
            pass


def safe_tqdm(*args, **kwargs) -> tqdm:
    """
    Cross-platform safe tqdm instance.

    Returns:
        Configured tqdm instance
    """
    stream = sys.stderr or sys.stdout
    disable = stream is None

    # Remove encoding from kwargs if present (tqdm doesn't support it)
    kwargs.pop("encoding", None)

    return tqdm(*args, file=stream or open(os.devnull, "w"), disable=disable, **kwargs)


def print_troubleshooting_info(
    chrome_executable: str = None,
    chromedriver_path: str = None,
    error: Exception = None
) -> None:
    """Print comprehensive troubleshooting information."""
    print("\n=== TROUBLESHOOTING INFORMATION ===")

    platform_info = get_platform_info()
    print(f"Platform: {platform_info['system']} {platform_info['release']}")
    print(f"Architecture: {platform_info['architecture']}")
    print(f"Python: {platform_info['python_version']}")

    if is_windows():
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            console_handle = kernel32.GetConsoleWindow()
            print(f"Console Available: {console_handle != 0}")
            print(f"Console Handle: {console_handle}")
        except Exception as e:
            print(f"Console Info Error: {e}")

    print(f"Chrome executable: {chrome_executable}")
    print(f"ChromeDriver: {chromedriver_path}")

    if error:
        print(f"Error Type: {type(error).__name__}")
        print(f"Error Message: {str(error)}")

    print("Framework: Cross-platform mode")
    print("=== END TROUBLESHOOTING INFO ===")
