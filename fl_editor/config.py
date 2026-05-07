"""Persistente Konfiguration fuer den FLAtlas Savegame Editor."""

import json
import os
from pathlib import Path

from .user_paths import user_config_dir

CONFIG_PATH = user_config_dir() / "config.json"


def _legacy_config_candidates() -> list[Path]:
    candidates: list[Path] = []
    appdata = str(os.environ.get("APPDATA", "") or "").strip()
    if appdata:
        candidates.append(Path(appdata) / "fl_editor" / "config.json")
    candidates.append(Path.home() / ".config" / "fl_editor" / "config.json")
    candidates.append(Path.home() / ".fl_editor" / "config.json")
    return candidates


def _migrate_legacy_config() -> None:
    if CONFIG_PATH.exists():
        return
    for legacy_path in _legacy_config_candidates():
        try:
            if not legacy_path.exists() or not legacy_path.is_file():
                continue
            raw = legacy_path.read_text(encoding="utf-8-sig")
            json.loads(raw)
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(raw, encoding="utf-8")
            return
        except Exception:
            continue


class Config:
    """Einfaches JSON-basiertes Key-Value-Konfigurationsobjekt."""

    def __init__(self):
        self._d: dict = {}
        _migrate_legacy_config()
        if CONFIG_PATH.exists():
            try:
                self._d = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
            except Exception:
                pass

    def get(self, key: str, default=None):
        return self._d.get(key, default)

    def set(self, key: str, value):
        self._d[key] = value
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(
                json.dumps(self._d, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            # Keep runtime settings in memory even if persistence is unavailable.
            pass
