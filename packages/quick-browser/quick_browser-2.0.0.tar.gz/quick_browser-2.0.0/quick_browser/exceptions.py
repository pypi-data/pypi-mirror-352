"""Custom exceptions for the Browser Framework."""


class BrowserError(Exception):
    """Base exception for browser-related errors."""

    pass


class DownloadError(BrowserError):
    """Exception for download errors."""

    pass


class SetupError(BrowserError):
    """Exception for setup errors."""

    pass


class LoginError(BrowserError):
    """Exception for login errors."""

    pass


class ValidationError(BrowserError):
    """Exception for validation errors."""

    pass


class ArchitectureError(SetupError):
    """Exception for architecture incompatibilities."""

    pass
