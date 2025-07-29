#!/usr/bin/env python
"""Package Build & Publish Script für Browser Framework."""

import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean():
    """Löscht Build-Artefakte."""
    import shutil

    dirs = ["build", "dist"]
    for d in dirs:
        if Path(d).exists():
            shutil.rmtree(d)
            logger.info(f"✓ {d}/ gelöscht")

    # .egg-info Verzeichnisse
    for egg_info in Path(".").glob("*.egg-info"):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            logger.info(f"✓ {egg_info} gelöscht")


def build():
    """Erstellt Package."""
    logger.info("📦 Erstelle Package...")
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        logger.info("✅ Package erfolgreich erstellt")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build fehlgeschlagen: {e}")
        return False


def publish_gitea():
    """Veröffentlicht auf Gitea."""
    token = os.getenv("GITEA_TOKEN")
    if not token:
        logger.error("❌ GITEA_TOKEN nicht gesetzt!")
        return False

    gitea_url = "https://gitea.noircoding.de"
    owner = "NoirPi"

    logger.info("🚀 Veröffentliche auf Gitea...")

    dist_path = Path("dist")
    success = True

    for file in dist_path.glob("*"):
        if file.suffix in [".whl", ".tar.gz"]:
            try:
                subprocess.run(
                    [
                        "curl",
                        "-X",
                        "PUT",
                        "-H",
                        f"Authorization: token {token}",
                        "-T",
                        str(file),
                        f"{gitea_url}/api/packages/{owner}/pypi/upload",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.info(f"   ✓ {file.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"   ❌ {file.name}: {e}")
                success = False

    if success:
        logger.info("✅ Package auf Gitea veröffentlicht")
        logger.info(
            f"📦 Installation: pip install --index-url {gitea_url}/api/packages/{owner}/pypi/simple/ quick-browser"
        )

    return success


def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "clean":
            clean()
        elif command == "build":
            clean()
            build()
        elif command == "gitea":
            clean()
            if build():
                publish_gitea()
        else:
            print("Verfügbare Commands: clean, build, gitea")
    else:
        print("Verwendung: python scripts/package.py [clean|build|gitea]")


if __name__ == "__main__":
    main()
