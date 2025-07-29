"""System-spezifische Utilities für Windows - 64-bit only."""

import ctypes
import os
import sys
from contextlib import contextmanager
from typing import Generator

from tqdm.auto import tqdm

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def _safe_set_console_title(title: str) -> bool:
    """
    Sicher Console-Titel setzen mit Unicode-Unterstützung.

    Args:
        title: Titel der Konsole

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        # Verwende SetConsoleTitleW für Unicode-Unterstützung
        # ctypes konvertiert Python-Strings automatisch zu wchar_t*
        result = kernel32.SetConsoleTitleW(title)
        return bool(result)
    except (OSError, ctypes.ArgumentError):
        # Fallback auf ANSI-Version
        try:
            # Konvertiere zu Bytes für SetConsoleTitleA
            title_bytes = title.encode("cp1252", errors="replace")
            result = kernel32.SetConsoleTitleA(title_bytes)
            return bool(result)
        except Exception:
            # Letzter Fallback: ignoriere Titel-Setzung
            return False


@contextmanager
def temp_console(title: str = "Download‑Konsole") -> Generator[None, None, None]:
    """
    Erstellt temporäre Konsole für Downloads mit automatischem Cleanup.
    Kompatibel mit Nuitka-Konsolenmodi.

    Args:
        title: Titel der Konsole

    Yields:
        None

    Raises:
        OSError: Wenn Konsole nicht erstellt werden kann
    """
    # Prüfen, ob bereits eine Konsole existiert (wichtig für --windows-console-mode=attach)
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    console_allocated = False

    if console_window == 0:  # Keine Konsole vorhanden
        if not kernel32.AllocConsole():
            raise OSError("AllocConsole failed")
        console_allocated = True
        _safe_set_console_title(title)
    elif title:  # Konsole existiert bereits, nur Titel setzen
        _safe_set_console_title(title)

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


def hide_console_if_needed(show_console: bool) -> None:
    """
    Versteckt Konsole wenn gewünscht.

    Args:
        show_console: True um Konsole sichtbar zu lassen
    """
    if not show_console and sys.platform == "win32":
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except Exception:
            pass  # Ignoriere Fehler beim Verstecken


def safe_tqdm(*args, **kwargs) -> tqdm:
    """
    Sichere tqdm-Instanz die auch ohne Stream funktioniert.

    Returns:
        Konfigurierte tqdm-Instanz
    """
    stream = sys.stderr or sys.stdout
    disable = stream is None

    # Entferne encoding aus kwargs falls vorhanden (tqdm unterstützt das nicht)
    kwargs.pop("encoding", None)

    return tqdm(*args, file=stream or open(os.devnull, "w"), disable=disable, **kwargs)
