#!/usr/bin/env python
"""
Version management for Quick Browser - Git-based versioning.
"""

import os
import subprocess
from typing import Any, Optional


def _run_git_command(cmd: list[str]) -> Optional[str]:
    """
    Execute Git command and return result.

    Args:
        cmd: Git command as list

    Returns:
        Command output or None on error
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd="."
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        return None


def _get_git_tag() -> Optional[str]:
    """
    Get current Git tag.

    Returns:
        Git tag (without 'v' prefix) or None
    """
    # Try to find current tag
    tag = _run_git_command(["git", "describe", "--tags", "--exact-match", "HEAD"])
    if tag:
        # Remove 'v' prefix if present
        return tag.lstrip('v')

    # Fallback: last tag + commits since tag
    tag_describe = _run_git_command(["git", "describe", "--tags", "--always"])
    if tag_describe and '-' in tag_describe:
        # Format: v1.2.0-5-g1a2b3c4 -> 1.2.0.dev5
        parts = tag_describe.split('-')
        if len(parts) >= 3:
            base_version = parts[0].lstrip('v')
            commits_ahead = parts[1]
            return f"{base_version}.dev{commits_ahead}"

    return None


def _get_git_sha() -> str:
    """
    Get short Git SHA.

    Returns:
        Short SHA (8 characters) or fallback
    """
    sha = _run_git_command(["git", "rev-parse", "--short=8", "HEAD"])
    if sha and len(sha) >= 6:
        return sha[:8]

    # Fallback when Git not available
    return "nogit000"


def _is_git_dirty() -> bool:
    """
    Check if Git tree is dirty.

    Returns:
        True if uncommitted changes present
    """
    status = _run_git_command(["git", "status", "--porcelain"])
    return bool(status and status.strip())


def get_version() -> str:
    """
    Get project version based on Git.

    Priority:
    1. Generated version file (from setuptools-scm)
    2. Environment variable (CI override)
    3. Git tag based version (clean)
    4. SHA-based fallback (clean)

    Returns:
        Clean version string (never "undefined", never with .dirty)
    """
    # Try generated version file first
    try:
        from ._version_generated import __version__ as generated_version
        return generated_version
    except ImportError:
        pass

    # CI/Build environment override
    ci_version = os.environ.get('SETUPTOOLS_SCM_PRETEND_VERSION')
    if ci_version and '.dirty' not in ci_version:
        return ci_version

    # Git tag based version (clean)
    _version = _get_git_tag()
    if _version:
        return _version.replace('.dirty', '')

    # Fallback: SHA-based version (clean)
    sha = _get_git_sha()
    return f"0.0.0+sha.{sha}"


def get_version_info() -> dict[str, Any]:
    """
    Return detailed version information.

    Returns:
        Dictionary with version details
    """
    _version = get_version()

    # Parse version components
    is_dev = ".dev" in _version
    is_dirty = False  # Always clean now
    has_local = "+" in _version

    # Split base version
    base_version = _version.split('.dev')[0].split('+')[0]
    version_parts = base_version.split('.')

    try:
        major = int(version_parts[0]) if len(version_parts) > 0 else 0
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0
    except (ValueError, IndexError):
        major = minor = patch = 0

    return {
        'version': _version,
        'major': major,
        'minor': minor,
        'patch': patch,
        'is_development': is_dev,
        'is_dirty': is_dirty,
        'is_release': not (is_dev or is_dirty or has_local),
        'git_sha': _get_git_sha(),
        'git_tag': _get_git_tag(),
    }


# Set version as module variable
__version__ = get_version()

if __name__ == "__main__":
    version = get_version()
    version_info = get_version_info()

    print(f"Version: {version}")
    print(f"Git SHA: {version_info['git_sha']}")
    print(f"Git Tag: {version_info['git_tag'] or 'None'}")
    print(f"Is Release: {version_info['is_release']}")
    print(f"Is Development: {version_info['is_development']}")
    print(f"Is Dirty: {version_info['is_dirty']}")
