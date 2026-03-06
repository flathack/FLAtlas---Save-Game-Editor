"""User-specific writable paths for FL Atlas editor data."""

from __future__ import annotations

import os
from pathlib import Path


def _is_dir_writable(path: Path) -> bool:
    probe = path / ".write_test.tmp"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def user_config_dir() -> Path:
    """Return a writable directory for user config/state files.

    Preference order:
    1) Windows `%APPDATA%\\fl_editor` (if available)
    2) POSIX-style `~/.config/fl_editor`
    3) `~/.fl_editor`
    """
    candidates: list[Path] = []
    appdata = str(os.environ.get("APPDATA", "") or "").strip()
    if appdata:
        candidates.append(Path(appdata) / "fl_editor")
    candidates.append(Path.home() / ".config" / "fl_editor")
    candidates.append(Path.home() / ".fl_editor")

    for path in candidates:
        try:
            if path.exists() and not path.is_dir():
                # Skip invalid paths where a file blocks directory creation.
                continue
            path.mkdir(parents=True, exist_ok=True)
            if not _is_dir_writable(path):
                continue
            return path
        except Exception:
            continue

    # Last resort to keep app startable even in constrained environments.
    return Path.cwd()
