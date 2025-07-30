"""Cross-platform system utilities für Windows und Linux."""

import ctypes
import os
import platform
import sys
from contextlib import contextmanager
from typing import Dict, Generator

from tqdm.auto import tqdm


def is_windows() -> bool:
    """Prüft ob Windows-System."""
    return sys.platform == "win32"


def is_linux() -> bool:
    """Prüft ob Linux-System."""
    return sys.platform.startswith("linux")


def get_platform_info() -> Dict[str, any]:
    """
    Ermittelt Platform-Informationen.

    Returns:
        Dictionary mit Platform-Details
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
    Windows-spezifische Console-Titel Setzung.

    Args:
        title: Titel der Konsole

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        # Verwende SetConsoleTitleW für Unicode-Unterstützung
        result = kernel32.SetConsoleTitleW(title)
        return bool(result)
    except (OSError, ctypes.ArgumentError):
        # Fallback auf ANSI-Version
        try:
            title_bytes = title.encode("cp1252", errors="replace")
            result = kernel32.SetConsoleTitleA(title_bytes)
            return bool(result)
        except Exception:
            return False


def _safe_set_console_title_linux(title: str) -> bool:
    """
    Linux-spezifische Terminal-Titel Setzung.

    Args:
        title: Titel des Terminals

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # ANSI escape sequence für Terminal-Titel
        if os.environ.get('TERM'):
            sys.stdout.write(f'\033]0;{title}\007')
            sys.stdout.flush()
            return True
        return False
    except Exception:
        return False


def safe_set_console_title(title: str) -> bool:
    """
    Cross-platform Console/Terminal-Titel Setzung.

    Args:
        title: Titel der Konsole/Terminal

    Returns:
        True bei Erfolg, False bei Fehler
    """
    if is_windows():
        return _safe_set_console_title_windows(title)
    elif is_linux():
        return _safe_set_console_title_linux(title)
    else:
        # Andere Plattformen - kein Titel-Support
        return False


@contextmanager
def temp_console_windows(title: str = "Download‑Konsole") -> Generator[None, None, None]:
    """
    Windows-spezifische temporäre Konsole.

    Args:
        title: Titel der Konsole

    Yields:
        None

    Raises:
        OSError: Wenn Konsole nicht erstellt werden kann
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    # Prüfen, ob bereits eine Konsole existiert
    console_window = kernel32.GetConsoleWindow()
    console_allocated = False

    if console_window == 0:  # Keine Konsole vorhanden
        if not kernel32.AllocConsole():
            raise OSError("AllocConsole failed")
        console_allocated = True
        safe_set_console_title(title)
    elif title:  # Konsole existiert bereits, nur Titel setzen
        safe_set_console_title(title)

    # Backup der ursprünglichen Streams
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # Versuche Console-Streams zu öffnen
        try:
            sys.stdout = open(
                "CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace"
            )
            sys.stderr = open(
                "CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace"
            )
        except OSError:
            # Fallback falls Console-Streams nicht verfügbar
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        yield

    finally:
        # Cleanup
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

        # Nur die Konsole freigeben, wenn wir sie selbst erstellt haben
        if console_allocated:
            try:
                kernel32.FreeConsole()
            except Exception:
                pass


@contextmanager
def temp_console_linux(title: str = "Download‑Terminal") -> Generator[None, None, None]:
    """
    Linux-spezifische temporäre Terminal-Konfiguration.

    Args:
        title: Titel des Terminals

    Yields:
        None
    """
    # Unter Linux verwenden wir das bestehende Terminal
    original_title_set = safe_set_console_title(title)

    try:
        yield
    finally:
        # Terminal-Titel zurücksetzen ist optional
        if original_title_set:
            safe_set_console_title("Terminal")


@contextmanager
def temp_console(title: str = "Download‑Konsole") -> Generator[None, None, None]:
    """
    Cross-platform temporäre Konsole/Terminal.

    Args:
        title: Titel der Konsole/Terminal

    Yields:
        None

    Raises:
        OSError: Wenn Konsole nicht erstellt werden kann (nur Windows)
    """
    if is_windows():
        with temp_console_windows(title):
            yield
    elif is_linux():
        with temp_console_linux(title):
            yield
    else:
        # Andere Plattformen - einfach durchlaufen
        yield


def hide_console_if_needed(show_console: bool) -> None:
    """
    Cross-platform Konsole verstecken wenn gewünscht.

    Args:
        show_console: True um Konsole sichtbar zu lassen
    """
    if not show_console:
        if is_windows():
            try:
                ctypes.windll.user32.ShowWindow(
                    ctypes.windll.kernel32.GetConsoleWindow(), 0
                )
            except Exception:
                pass  # Ignoriere Fehler beim Verstecken
        elif is_linux():
            # Unter Linux können wir das Terminal nicht verstecken
            # Das ist auch nicht üblich - Linux-User erwarten ein Terminal
            pass


def safe_tqdm(*args, **kwargs) -> tqdm:
    """
    Cross-platform sichere tqdm-Instanz.

    Returns:
        Konfigurierte tqdm-Instanz
    """
    stream = sys.stderr or sys.stdout
    disable = stream is None

    # Entferne encoding aus kwargs falls vorhanden (tqdm unterstützt das nicht)
    kwargs.pop("encoding", None)

    return tqdm(*args, file=stream or open(os.devnull, "w"), disable=disable, **kwargs)
