"""Internationalisation helper for FL Atlas.

Translations live in a bundled JSON file next to this module
(``translations.json``).  A user-level override is loaded from the
app-specific user config directory only when it already exists.

Usage::

    from fl_editor.i18n import tr, set_language, get_language

    label.setText(tr("btn.save"))
    status.showMessage(tr("status.universe_loaded").format(count=42))
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from .user_paths import user_config_dir

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_BUNDLED_FILE = Path(__file__).with_name("translations.json")
_USER_DIR = user_config_dir()
_USER_FILE = _USER_DIR / "translations.json"

# ---------------------------------------------------------------------------
# Module state
# ---------------------------------------------------------------------------
_translations: Dict[str, Dict[str, str]] = {}
_current_lang: str = "en"


def _load_translations() -> None:
    """(Re)load translations from disk.

    The bundled translation file is always loaded.  A user file takes priority
    only when it already exists; the Savegame Editor must not create or copy
    FL Atlas V1 translation files into its own config directory.
    """
    global _translations

    bundled_data: Dict[str, Dict[str, str]] = {}
    user_data: Dict[str, Dict[str, str]] = {}

    if _BUNDLED_FILE.exists():
        try:
            with open(_BUNDLED_FILE, "r", encoding="utf-8") as fh:
                bundled_data = json.load(fh)
        except Exception:
            bundled_data = {}

    if _USER_FILE.exists():
        try:
            with open(_USER_FILE, "r", encoding="utf-8") as fh:
                user_data = json.load(fh)
        except Exception:
            user_data = {}

    merged: Dict[str, Dict[str, str]] = {}
    for lang in set(bundled_data.keys()) | set(user_data.keys()):
        base_lang = bundled_data.get(lang, {})
        user_lang = user_data.get(lang, {})
        merged[lang] = {**base_lang, **user_lang}
    _translations = merged


# Load on import
_load_translations()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def tr(key: str) -> str:
    """Return the translated string for *key* in the current language.

    Falls back to German (``"de"``), then to the raw key itself so that
    missing translations are immediately visible during development.
    """
    lang_dict = _translations.get(_current_lang)
    if lang_dict and key in lang_dict:
        return lang_dict[key]
    # Fallback: German
    de_dict = _translations.get("de")
    if de_dict and key in de_dict:
        return de_dict[key]
    return key  # last resort


def set_language(lang: str) -> None:
    """Switch the active language (e.g. ``"de"`` or ``"en"``)."""
    global _current_lang
    _current_lang = lang


def get_language() -> str:
    """Return the active language code."""
    return _current_lang


def available_languages() -> list[str]:
    """Return sorted list of language codes present in the translation file."""
    return sorted(_translations.keys())


def reload_translations() -> None:
    """Force-reload translations from disk (e.g. after external edits)."""
    _load_translations()
