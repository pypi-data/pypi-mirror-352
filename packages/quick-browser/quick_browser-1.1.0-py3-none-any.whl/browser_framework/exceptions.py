"""Custom Exceptions für das Browser Framework."""


class BrowserError(Exception):
    """Base Exception für Browser-bezogene Fehler."""

    pass


class DownloadError(BrowserError):
    """Exception für Download-Fehler."""

    pass


class SetupError(BrowserError):
    """Exception für Setup-Fehler."""

    pass


class LoginError(BrowserError):
    """Exception für Login-Fehler."""

    pass


class ValidationError(BrowserError):
    """Exception für Validierungsfehler."""

    pass


class ArchitectureError(SetupError):
    """Exception für Architektur-Inkompatibilitäten."""

    pass
