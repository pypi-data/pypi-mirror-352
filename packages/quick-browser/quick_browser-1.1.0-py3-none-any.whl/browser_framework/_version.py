#!/usr/bin/env python
"""
Version management für Quick Browser - EINFACH UND FUNKTIONAL.
"""

# FUCK GIT VERSIONING - EINFACHE MANUELLE VERSION
__version__ = "1.1.0"

# Einfache Version Info
__version_info__ = {
    'version': __version__,
    'major': 1,
    'minor': 1,
    'patch': 0,
    'pre_release': None,
    'local': None,
    'is_release': True,
    'is_development': False,
}

def get_version() -> str:
    """Gibt die fixe Version zurück - KEIN GIT BULLSHIT."""
    return __version__

def get_version_info() -> dict:
    """Gibt Version-Info zurück."""
    return __version_info__

if __name__ == "__main__":
    print(f"Version: {__version__}")
    print("Git Versioning: DEAKTIVIERT (zum Glück!)")
