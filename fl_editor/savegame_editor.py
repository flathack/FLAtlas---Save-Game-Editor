"""Savegame editor module for FL Atlas.

This module can be used from MainWindow integration and can also be started standalone.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import json
import webbrowser
from urllib import request as urlrequest, error as urlerror
from pathlib import Path

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QIcon, QPixmap, QActionGroup
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGraphicsScene,
    QGroupBox,
    QGraphicsView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QSizePolicy,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QSplashScreen,
)

from .i18n import tr, set_language, get_language, available_languages
from .config import Config, CONFIG_PATH
from .parser import FLParser, find_all_systems
from .path_utils import ci_find, ci_resolve
from .dll_resources import DllStringResolver

SAVEGAME_EDITOR_VERSION = "v0.1.0"
DISCORD_INVITE_URL = "https://discord.gg/RENtMMcc"
BUG_REPORT_URL = "https://github.com/flathack/FLAtlas/issues"
GITHUB_RELEASES_API = "https://api.github.com/repos/flathack/FLAtlas---Save-Game-Editor/releases?per_page=30"

THEME_ORDER = [
    "Standard",
    "Light",
    "Dark",
    "High Contrast",
    "Linux KDE",
]
THEME_ORDER_SET = {str(n) for n in THEME_ORDER}

THEME_STYLES: dict[str, str] = {
    "Standard": """
QDialog { background-color: #12161f; color: #e8edf5; }
QMenuBar, QMenu { background: #171c26; color: #e8edf5; }
QMenuBar::item:selected, QMenu::item:selected { background: #2f6fed; color: #ffffff; border-radius: 6px; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #e8edf5; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #8893a6; }
QGroupBox { border: 1px solid #2f3b51; border-radius: 10px; margin-top: 9px; padding-top: 8px; background: #151b26; }
QPushButton { background: #1d2533; border: 1px solid #3b4d6a; border-radius: 8px; padding: 6px 12px; color: #eef3fb; }
QPushButton:hover { background: #243048; border-color: #5f7fb8; }
QPushButton:pressed { background: #1b2740; }
QPushButton:disabled { color: #7f8aa0; border-color: #313c50; background: #1a202c; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #0f141d; color: #e8edf5; border: 1px solid #3b4d6a; border-radius: 8px; min-height: 24px; selection-background-color: #2f6fed; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #8791a4; border-color: #2a3447; background: #141a24; }
QTabWidget::pane { border: 1px solid #33425c; border-radius: 10px; top: -1px; background: #121923; }
QTabBar::tab { background: #1a2230; border: 1px solid #33425c; border-radius: 8px; padding: 6px 12px; margin-right: 2px; color: #cfd9e8; }
QTabBar::tab:selected { background: #243247; color: #ffffff; border-color: #5f7fb8; }
QTableWidget { gridline-color: #2a364b; background: #0f141d; alternate-background-color: #141a25; }
QHeaderView::section { background: #1b2332; border: 1px solid #2a364b; padding: 4px; }
QScrollBar:vertical, QScrollBar:horizontal { background: #151c27; }
""",
    "Light": """
QDialog { background-color: #f5f7fb; color: #111827; }
QMenuBar, QMenu { background: #f5f7fb; color: #111827; }
QMenuBar::item:selected, QMenu::item:selected { background: #2563eb; color: #ffffff; border-radius: 6px; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #111827; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #7a8598; }
QGroupBox { border: 1px solid #d5dbe6; border-radius: 10px; margin-top: 9px; padding-top: 8px; background: #ffffff; }
QPushButton { background: #edf2ff; border: 1px solid #c3d1ee; border-radius: 8px; padding: 6px 12px; color: #111827; }
QPushButton:hover { background: #e3ebff; border-color: #98afe0; }
QPushButton:pressed { background: #dae5ff; }
QPushButton:disabled { color: #8a96aa; border-color: #d3dcea; background: #f2f5fa; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #111827; border: 1px solid #c8d1e0; border-radius: 8px; min-height: 24px; selection-background-color: #2563eb; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #8a96aa; border-color: #d8dfea; background: #f4f7fb; }
QTabWidget::pane { border: 1px solid #d0d8e5; border-radius: 10px; top: -1px; background: #ffffff; }
QTabBar::tab { background: #eef3ff; border: 1px solid #d0d8e5; border-radius: 8px; padding: 6px 12px; margin-right: 2px; color: #334155; }
QTabBar::tab:selected { background: #ffffff; color: #111827; border-color: #9fb5e4; }
QTableWidget { gridline-color: #e1e7f0; background: #ffffff; alternate-background-color: #f8faff; }
QHeaderView::section { background: #f0f4fb; border: 1px solid #e1e7f0; padding: 4px; }
""",
    "Dark": """
QDialog { background-color: #0f131b; color: #e7edf8; }
QMenuBar, QMenu { background: #141a24; color: #e7edf8; }
QMenuBar::item:selected, QMenu::item:selected { background: #3b82f6; color: #ffffff; border-radius: 6px; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #e7edf8; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #8c97aa; }
QGroupBox { border: 1px solid #2a3448; border-radius: 10px; margin-top: 9px; padding-top: 8px; background: #141a24; }
QPushButton { background: #1a2434; border: 1px solid #354967; border-radius: 8px; padding: 6px 12px; color: #eef3fd; }
QPushButton:hover { background: #223049; border-color: #6687c0; }
QPushButton:pressed { background: #1f2a40; }
QPushButton:disabled { color: #8994a8; border-color: #2d3a51; background: #1a222f; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #0c1119; color: #e7edf8; border: 1px solid #354967; border-radius: 8px; min-height: 24px; selection-background-color: #3b82f6; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #8c97aa; border-color: #2b3850; background: #131a25; }
QTabWidget::pane { border: 1px solid #2d3a51; border-radius: 10px; top: -1px; background: #111823; }
QTabBar::tab { background: #192232; border: 1px solid #2d3a51; border-radius: 8px; padding: 6px 12px; margin-right: 2px; color: #c4cfdf; }
QTabBar::tab:selected { background: #24344d; color: #ffffff; border-color: #6687c0; }
QTableWidget { gridline-color: #263449; background: #0d121a; alternate-background-color: #121a26; }
QHeaderView::section { background: #182233; border: 1px solid #263449; padding: 4px; }
QScrollBar:vertical, QScrollBar:horizontal { background: #141a24; }
""",
    "High Contrast": """
QDialog { background-color: #000000; color: #ffffff; }
QMenuBar, QMenu { background: #000000; color: #ffffff; border: 1px solid #ffffff; }
QMenuBar::item:selected, QMenu::item:selected { background: #ffff00; color: #000000; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #ffffff; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #bfbfbf; }
QGroupBox { border: 2px solid #ffffff; border-radius: 0px; margin-top: 10px; padding-top: 8px; background: #000000; }
QPushButton { background: #000000; border: 2px solid #ffffff; border-radius: 0px; padding: 6px 12px; color: #ffffff; }
QPushButton:hover { border-color: #ffff00; color: #ffff00; }
QPushButton:pressed { background: #ffff00; color: #000000; }
QPushButton:disabled { color: #bfbfbf; border-color: #9f9f9f; background: #000000; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #000000;
    color: #ffffff;
    border: 2px solid #ffffff;
    border-radius: 0px;
    min-height: 24px;
    selection-background-color: #ffff00;
    selection-color: #000000;
}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {
    color: #bfbfbf;
    border-color: #9f9f9f;
    background: #000000;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QPushButton:focus, QTableWidget:focus {
    border: 3px solid #00ffff;
}
QTabWidget::pane { border: 2px solid #ffffff; border-radius: 0px; top: -1px; background: #000000; }
QTabBar::tab { background: #000000; border: 2px solid #ffffff; border-radius: 0px; padding: 6px 12px; margin-right: 2px; color: #ffffff; }
QTabBar::tab:selected { background: #ffff00; color: #000000; border-color: #ffffff; }
QTableWidget {
    gridline-color: #ffffff;
    background: #000000;
    alternate-background-color: #0f0f0f;
    color: #ffffff;
    selection-background-color: #ffff00;
    selection-color: #000000;
}
QHeaderView::section { background: #000000; border: 2px solid #ffffff; color: #ffffff; padding: 4px; }
QScrollBar:vertical, QScrollBar:horizontal { background: #000000; border: 1px solid #ffffff; }
QToolTip { background: #000000; color: #ffffff; border: 1px solid #ffffff; }
""",
    "Windows XP": """
QDialog { background-color: #ece9d8; color: #1f1f1f; }
QMenuBar, QMenu { background: #ece9d8; color: #1f1f1f; }
QMenuBar::item:selected, QMenu::item:selected { background: #316ac5; color: #ffffff; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #1f1f1f; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #7b7b7b; }
QGroupBox { border: 1px solid #7f9db9; margin-top: 8px; padding-top: 6px; background: #f5f2e5; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f9f8f3, stop:1 #dcd9c8); border: 1px solid #7f9db9; padding: 4px 10px; }
QPushButton:hover { border-color: #3c7fb1; }
QPushButton:disabled { color: #808080; border-color: #9a9a9a; background: #e1dfd2; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #1f1f1f; border: 1px solid #7f9db9; min-height: 22px; selection-background-color: #316ac5; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #7b7b7b; background: #f0f0f0; }
QTabWidget::pane { border: 1px solid #7f9db9; top: -1px; }
QTabBar::tab { background: #e3e9f7; border: 1px solid #7f9db9; padding: 5px 10px; margin-right: 1px; }
QTabBar::tab:selected { background: #ffffff; }
QTableWidget { gridline-color: #b5c5db; background: #ffffff; alternate-background-color: #f7f9ff; }
QHeaderView::section { background: #dbe6f7; border: 1px solid #a8bcd9; padding: 4px; }
""",
    "Windows 7": """
QDialog { background-color: #edf2fb; color: #1b1d1f; }
QMenuBar, QMenu { background: #edf2fb; color: #1b1d1f; }
QMenuBar::item:selected, QMenu::item:selected { background: #2f75d6; color: #ffffff; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #1b1d1f; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #6f7785; }
QGroupBox { border: 1px solid #9bb7df; border-radius: 4px; margin-top: 8px; padding-top: 6px; background: #f6f9ff; }
QPushButton { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff, stop:1 #d6e3f6); border: 1px solid #8ca9d1; border-radius: 3px; padding: 5px 11px; }
QPushButton:hover { border-color: #4f7fbe; }
QPushButton:disabled { color: #7f8898; border-color: #aeb8ca; background: #e9edf5; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #1b1d1f; border: 1px solid #8ca9d1; border-radius: 2px; min-height: 22px; selection-background-color: #2f75d6; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #6f7785; background: #f1f4f9; border-color: #bec8da; }
QTabWidget::pane { border: 1px solid #9bb7df; }
QTabBar::tab { background: #dce8f9; border: 1px solid #9bb7df; padding: 5px 10px; }
QTabBar::tab:selected { background: #ffffff; }
QTableWidget { gridline-color: #c3d0e4; background: #ffffff; alternate-background-color: #f7faff; }
QHeaderView::section { background: #e4eefc; border: 1px solid #bfd0ea; padding: 4px; }
""",
    "Windows 10": """
QDialog { background-color: #f2f2f2; color: #111111; }
QMenuBar, QMenu { background: #f2f2f2; color: #111111; }
QMenuBar::item:selected, QMenu::item:selected { background: #0078d7; color: #ffffff; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #111111; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #6a6a6a; }
QGroupBox { border: 1px solid #b8b8b8; margin-top: 8px; padding-top: 6px; background: #f9f9f9; }
QPushButton { background: #f3f3f3; border: 1px solid #adadad; border-radius: 2px; padding: 5px 12px; }
QPushButton:hover { border-color: #0078d7; }
QPushButton:disabled { color: #8b8b8b; background: #ededed; border-color: #c9c9c9; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #111111; border: 1px solid #9c9c9c; min-height: 22px; selection-background-color: #0078d7; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #7a7a7a; background: #f3f3f3; border-color: #c7c7c7; }
QTabWidget::pane { border: 1px solid #b8b8b8; top: -1px; }
QTabBar::tab { background: #e9e9e9; border: 1px solid #b8b8b8; padding: 5px 11px; }
QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
QTableWidget { gridline-color: #d3d3d3; background: #ffffff; alternate-background-color: #fafafa; }
QHeaderView::section { background: #f0f0f0; border: 1px solid #d3d3d3; padding: 4px; }
""",
    "Windows 11": """
QDialog { background-color: #f6f8fc; color: #101828; }
QMenuBar, QMenu { background: #f6f8fc; color: #101828; }
QMenuBar::item:selected, QMenu::item:selected { background: #2563eb; color: #ffffff; border-radius: 6px; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #101828; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #76839a; }
QGroupBox { border: 1px solid #c8d2e1; border-radius: 10px; margin-top: 10px; padding-top: 8px; }
QGroupBox::title { left: 10px; padding: 0 4px; }
QPushButton { background: #e8efff; border: 1px solid #b7c5e2; border-radius: 8px; padding: 6px 13px; }
QPushButton:hover { background: #dce7ff; border-color: #7ea2df; }
QPushButton:disabled { color: #8794ab; background: #eef2f8; border-color: #d4deec; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #101828; border: 1px solid #c3cfdf; border-radius: 8px; min-height: 24px; selection-background-color: #2563eb; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #7e8ca2; background: #f2f5fa; border-color: #d8e0ec; }
QTabWidget::pane { border: 1px solid #c3cfdf; border-radius: 10px; top: -1px; }
QTabBar::tab { background: #edf2ff; border: 1px solid #c3cfdf; border-radius: 8px; padding: 6px 12px; margin-right: 2px; }
QTabBar::tab:selected { background: #ffffff; }
QTableWidget { gridline-color: #d8e0ec; background: #ffffff; alternate-background-color: #f7f9fd; }
QHeaderView::section { background: #eef3fb; border: 1px solid #d8e0ec; padding: 4px; }
""",
    "Linux KDE": """
QDialog { background-color: #1f2530; color: #e6edf7; }
QMenuBar, QMenu { background: #232a36; color: #e6edf7; }
QMenuBar::item:selected, QMenu::item:selected { background: #3d7ea6; color: #ffffff; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #e6edf7; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #94a3ba; }
QGroupBox { border: 1px solid #4f6179; border-radius: 5px; margin-top: 8px; padding-top: 6px; }
QPushButton { background: #2a3444; border: 1px solid #5f7290; border-radius: 4px; padding: 5px 10px; color: #f0f4fb; }
QPushButton:hover { background: #314157; border-color: #79a3d1; }
QPushButton:disabled { color: #95a2b8; border-color: #4d607d; background: #2a3240; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #121821; color: #e6edf7; border: 1px solid #5f7290; min-height: 22px; selection-background-color: #3d7ea6; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #97a5bc; background: #1b2230; border-color: #485a74; }
QTabWidget::pane { border: 1px solid #5f7290; }
QTabBar::tab { background: #2b3648; border: 1px solid #5f7290; padding: 5px 10px; }
QTabBar::tab:selected { background: #3a4b63; }
QTableWidget { gridline-color: #3d4d64; background: #121821; alternate-background-color: #18202c; }
QHeaderView::section { background: #293549; border: 1px solid #43556f; padding: 4px; }
""",
    "Gnome": """
QDialog { background-color: #f6f5f4; color: #241f31; }
QMenuBar, QMenu { background: #f6f5f4; color: #241f31; }
QMenuBar::item:selected, QMenu::item:selected { background: #3584e4; color: #ffffff; border-radius: 6px; }
QLabel, QGroupBox::title, QAbstractButton, QTableWidget, QHeaderView::section { color: #241f31; }
QLabel:disabled, QAbstractButton:disabled, QGroupBox::title:disabled { color: #77767b; }
QGroupBox { border: 1px solid #c6c4c0; border-radius: 12px; margin-top: 9px; padding-top: 8px; }
QPushButton { background: #ffffff; border: 1px solid #c6c4c0; border-radius: 10px; padding: 6px 13px; }
QPushButton:hover { border-color: #3584e4; }
QPushButton:disabled { color: #8a8891; border-color: #d8d6d3; background: #f1f1f1; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background: #ffffff; color: #241f31; border: 1px solid #c6c4c0; border-radius: 10px; min-height: 24px; selection-background-color: #3584e4; selection-color: #ffffff; }
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #807d89; background: #f2f2f1; border-color: #d8d6d3; }
QTabWidget::pane { border: 1px solid #c6c4c0; border-radius: 12px; }
QTabBar::tab { background: #eceae8; border: 1px solid #c6c4c0; border-radius: 9px; padding: 6px 12px; margin-right: 2px; }
QTabBar::tab:selected { background: #ffffff; border-color: #3584e4; }
QTableWidget { gridline-color: #dad8d4; background: #ffffff; alternate-background-color: #f7f6f5; }
QHeaderView::section { background: #efeeec; border: 1px solid #dad8d4; padding: 4px; }
""",
}


def _tr_or(key: str, fallback: str) -> str:
    txt = str(tr(key) or "").strip()
    return fallback if (not txt or txt == key) else txt


def _parse_version_tag(tag: str) -> tuple[list[int], list[tuple[int, int | str]], bool]:
    raw = str(tag or "").strip().lstrip("vV")
    if not raw:
        return [0], [], False
    core, _sep, pre = raw.partition("-")
    core_parts: list[int] = []
    for part in core.split("."):
        try:
            core_parts.append(int(part))
        except Exception:
            core_parts.append(0)
    pre_parts: list[tuple[int, int | str]] = []
    if pre:
        for part in re.split(r"[.\-]+", pre):
            p = str(part or "").strip()
            if not p:
                continue
            if p.isdigit():
                pre_parts.append((0, int(p)))  # numeric
            else:
                pre_parts.append((1, p.lower()))  # alnum
    return core_parts, pre_parts, bool(pre_parts)


def _is_version_newer(latest_tag: str, current_tag: str) -> bool:
    la_core, la_pre, la_is_pre = _parse_version_tag(latest_tag)
    cu_core, cu_pre, cu_is_pre = _parse_version_tag(current_tag)
    max_len = max(len(la_core), len(cu_core))
    for i in range(max_len):
        lv = la_core[i] if i < len(la_core) else 0
        cv = cu_core[i] if i < len(cu_core) else 0
        if lv != cv:
            return lv > cv
    if la_is_pre != cu_is_pre:
        return not la_is_pre  # stable > prerelease
    if not la_is_pre and not cu_is_pre:
        return False
    max_pre = max(len(la_pre), len(cu_pre))
    for i in range(max_pre):
        if i >= len(la_pre):
            return False
        if i >= len(cu_pre):
            return True
        lt, lv = la_pre[i]
        ct, cv = cu_pre[i]
        if lt != ct:
            return lt < ct  # numeric < string
        if lv != cv:
            return lv > cv
    return False


def _fetch_latest_release() -> dict[str, str] | None:
    req = urlrequest.Request(
        GITHUB_RELEASES_API,
        headers={
            "User-Agent": "FLAtlas-Savegame-Editor",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urlrequest.urlopen(req, timeout=5) as resp:
            raw = resp.read()
    except (urlerror.URLError, TimeoutError, OSError):
        return None
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception:
        return None
    if not isinstance(data, list):
        return None
    if not data:
        return {}
    best: dict[str, str] | None = None
    for row in data:
        if not isinstance(row, dict):
            continue
        if bool(row.get("draft")):
            continue
        tag = str(row.get("tag_name") or "").strip()
        if not tag:
            continue
        cand = {
            "tag": tag,
            "name": str(row.get("name") or tag),
            "url": str(row.get("html_url") or ""),
            "type": "Pre-release" if bool(row.get("prerelease")) else "Release",
        }
        if best is None or _is_version_newer(cand["tag"], best["tag"]):
            best = cand
    return best


def _check_for_updates_popup(parent: QWidget | None = None, *, verbose: bool = False) -> None:
    latest = _fetch_latest_release()
    if not latest:
        if isinstance(latest, dict) and not latest:
            if verbose:
                QMessageBox.information(
                    parent,
                    tr("savegame_editor.title"),
                    tr("savegame_editor.update.no_releases"),
                )
            return
        if verbose:
            QMessageBox.information(
                parent,
                tr("savegame_editor.title"),
                tr("savegame_editor.update.check_failed"),
            )
        return
    latest_tag = str(latest.get("tag") or "").strip()
    if not latest_tag or not _is_version_newer(latest_tag, SAVEGAME_EDITOR_VERSION):
        if verbose:
            QMessageBox.information(
                parent,
                tr("savegame_editor.title"),
                tr("savegame_editor.update.current").format(version=SAVEGAME_EDITOR_VERSION),
            )
        return
    title = tr("savegame_editor.update.title")
    text = (
        tr("savegame_editor.update.text").format(
            release_type=str(latest.get("type", "release") or "release"),
            current=SAVEGAME_EDITOR_VERSION,
            latest=latest_tag,
            name=str(latest.get("name", latest_tag) or latest_tag),
        )
    )
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(text)
    open_btn = box.addButton(tr("savegame_editor.update.open"), QMessageBox.AcceptRole)
    box.addButton(tr("savegame_editor.update.later"), QMessageBox.RejectRole)
    box.exec()
    if box.clickedButton() is open_btn:
        url = str(latest.get("url") or "").strip()
        if url:
            try:
                webbrowser.open(url)
            except Exception:
                pass


class _SavegameKnownMapView(QGraphicsView):
    """Known-Objects map view with auto-fit and mouse-wheel zoom."""

    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None):
        super().__init__(scene, parent)
        self._base_rect = QRectF()
        self._zoom_factor = 1.0
        self._min_zoom = 0.25
        self._max_zoom = 8.0
        self.on_system_click = None
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def set_base_rect(self, rect: QRectF) -> None:
        self._base_rect = QRectF(rect)
        self._apply_view_transform()

    def reset_zoom(self) -> None:
        self._zoom_factor = 1.0
        self._apply_view_transform()

    def _apply_view_transform(self) -> None:
        if self._base_rect.isNull() or self._base_rect.width() <= 0 or self._base_rect.height() <= 0:
            return
        self.resetTransform()
        self.fitInView(self._base_rect, Qt.KeepAspectRatio)
        if abs(self._zoom_factor - 1.0) > 1e-6:
            self.scale(self._zoom_factor, self._zoom_factor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_view_transform()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            return
        step = 1.15 if delta > 0 else (1.0 / 1.15)
        self._zoom_factor = max(self._min_zoom, min(self._max_zoom, self._zoom_factor * step))
        self._apply_view_transform()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and callable(self.on_system_click):
            item = self.itemAt(event.pos())
            if item is not None:
                system_key = str(item.data(0) or "").strip()
                if system_key:
                    try:
                        self.on_system_click(system_key)
                    except Exception:
                        pass
                    event.accept()
                    return
        super().mousePressEvent(event)


class _SavegameEditorHost(QMainWindow):
    """Minimal host for standalone savegame editor."""

    def __init__(self):
        super().__init__()
        self._cfg = Config()
        lang = str(self._cfg.get("settings.language", "") or "").strip()
        if lang:
            try:
                set_language(lang)
            except Exception:
                pass
        self._parser = FLParser()
        self._cached_factions: list[str] = []
        self._faction_label_to_nick: dict[str, str] = {}
        self._faction_nick_to_label: dict[str, str] = {}
        self._savegame_nickname_labels_cache: dict[str, dict[str, str]] = {}
        self._savegame_numeric_id_map_cache: dict[str, dict[int, str]] = {}
        self._savegame_item_data_cache: dict[str, dict[str, object]] = {}
        self._savegame_jump_connections_cache: dict[str, dict[str, object]] = {}
        self._savegame_system_display_cache: dict[str, dict[str, str]] = {}
        self._flhash_table: list[int] | None = None
        self._dll_resolver = DllStringResolver()
        self._dll_lookup_key = ""
        self.setStatusBar(None)
        icon_path = Path(__file__).with_name("images") / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def statusBar(self):
        sb = super().statusBar()
        if sb is None:
            from PySide6.QtWidgets import QStatusBar

            sb = QStatusBar(self)
            self.setStatusBar(sb)
        return sb

    def _primary_game_path(self) -> str:
        p = str(self._cfg.get("settings.savegame_game_path", "") or "").strip()
        if p and Path(p).exists():
            return p
        return ""

    def _fallback_game_path(self) -> str:
        return self._primary_game_path()

    def _default_savegame_editor_dir(self) -> Path:
        cfg_dir = str(self._cfg.get("settings.savegame_path", "") or "").strip()
        if cfg_dir:
            p = Path(cfg_dir)
            if p.exists():
                return p
        if os.name == "nt":
            userprofile = str(os.environ.get("USERPROFILE", "") or "").strip()
            if userprofile:
                p = Path(userprofile) / "Documents" / "My Games" / "Freelancer" / "Accts" / "SinglePlayer"
                if p.exists():
                    return p
        p = Path.home() / "Documents" / "My Games" / "Freelancer" / "Accts" / "SinglePlayer"
        if p.exists():
            return p
        return Path.home()

    def _default_savegame_editor_game_path(self) -> str:
        cfg_path = str(self._cfg.get("settings.savegame_game_path", "") or "").strip()
        if cfg_path and Path(cfg_path).exists():
            return cfg_path
        return ""

    @staticmethod
    def _path_from_text(raw_path: str) -> Path:
        txt = str(raw_path or "").strip()
        if not txt:
            return Path("")
        expanded = os.path.expanduser(os.path.expandvars(txt))
        try:
            return Path(expanded)
        except Exception:
            return Path(txt)

    @staticmethod
    def _dedupe_paths(paths: list[Path]) -> list[Path]:
        out: list[Path] = []
        seen: set[str] = set()
        for p in paths:
            try:
                key = str(p.resolve()).lower()
            except Exception:
                key = str(p).lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
        return out

    def _canonical_savegame_dir_from_input(self, raw_path: str) -> Path:
        base = self._path_from_text(raw_path)
        if not str(base):
            return base
        if base.is_file():
            base = base.parent
        suffix = ("My Games", "Freelancer", "Accts", "SinglePlayer")

        def _completed_from_tail(path: Path) -> Path:
            lower_parts = [str(p).lower() for p in path.parts]
            target = [str(p).lower() for p in suffix]
            max_overlap = min(len(lower_parts), len(target))
            overlap = 0
            for n in range(max_overlap, 0, -1):
                if lower_parts[-n:] == target[:n]:
                    overlap = n
                    break
            return path.joinpath(*suffix[overlap:])

        candidates: list[Path] = [_completed_from_tail(base), base.joinpath(*suffix), base]
        lname = base.name.lower()
        if lname == "documents":
            candidates.append(base.joinpath(*suffix))
        if lname == "my games":
            candidates.append(base / "Freelancer" / "Accts" / "SinglePlayer")
        if lname == "freelancer":
            candidates.append(base / "Accts" / "SinglePlayer")
        if lname == "accts":
            candidates.append(base / "SinglePlayer")
        for anc in [base] + list(base.parents):
            if anc.name.lower() == "documents":
                candidates.append(anc.joinpath(*suffix))
        candidates = self._dedupe_paths(candidates)
        for cand in candidates:
            if cand.exists() and cand.is_dir():
                return cand
        return candidates[0] if candidates else base

    def _find_freelancer_exe(self, game_root: Path) -> Path | None:
        root = Path(game_root)
        if not root.exists():
            return None
        if root.is_file():
            if root.name.lower() == "freelancer.exe":
                return root
            return None
        exe_ci = ci_resolve(root, "EXE/Freelancer.exe")
        if exe_ci is not None and exe_ci.exists() and exe_ci.is_file():
            return exe_ci
        exe_exact = root / "EXE" / "Freelancer.exe"
        if exe_exact.exists() and exe_exact.is_file():
            return exe_exact
        if root.name.lower() == "exe":
            exe_in = ci_find(root, "Freelancer.exe")
            if exe_in is not None and exe_in.exists() and exe_in.is_file():
                return exe_in
        return None

    def _canonical_game_dir_from_input(self, raw_path: str) -> Path:
        base = self._path_from_text(raw_path)
        if not str(base):
            return base
        if base.is_file() and base.name.lower() == "freelancer.exe":
            par = base.parent
            if par.name.lower() == "exe":
                return par.parent
            return par
        if base.is_dir() and base.name.lower() == "exe":
            exe_in = self._find_freelancer_exe(base)
            if exe_in is not None:
                return base.parent

        # Prefer nearest valid ancestor first.
        for cand in [base] + list(base.parents):
            if cand.exists() and cand.is_dir() and self._find_freelancer_exe(cand) is not None:
                return cand

        # Limited downward search for EXE/Freelancer.exe when user entered a partial path.
        if base.exists() and base.is_dir():
            max_depth = 5
            max_dirs = 2000
            scanned = 0
            queue: list[tuple[Path, int]] = [(base, 0)]
            while queue and scanned < max_dirs:
                cur, depth = queue.pop(0)
                scanned += 1
                if self._find_freelancer_exe(cur) is not None:
                    return cur
                if depth >= max_depth:
                    continue
                try:
                    for ch in cur.iterdir():
                        if ch.is_dir():
                            queue.append((ch, depth + 1))
                except Exception:
                    continue
        return base

    @staticmethod
    def _savegame_editor_cache_key(game_path: str) -> str:
        gp = str(game_path or "").strip()
        if not gp:
            return ""
        try:
            return str(Path(gp).resolve()).lower()
        except Exception:
            return gp.lower()

    def _resolve_game_path_case_insensitive(self, game_path: str, rel_path: str) -> Path | None:
        gp = Path(str(game_path or "").strip())
        if not gp.exists():
            return None
        return ci_resolve(gp, rel_path)

    def _read_text_best_effort(self, path: Path) -> str:
        raw = path.read_bytes()
        if raw.startswith(b"FLS1"):
            # GENE cipher used by encrypted Freelancer saves (FLS1 header).
            gene = (0x47, 0x65, 0x6E, 0x65)
            out = bytearray()
            i = 0
            for b in raw[4:]:
                gene_cipher = ((gene[i % 4] + i) % 256) & 0xFF
                out.append(int(b) ^ (gene_cipher | 0x80))
                i += 1
            dec = bytes(out)
            for enc in ("utf-8", "cp1252", "latin1"):
                try:
                    txt = dec.decode(enc)
                    return txt.replace("\x85", "\n").replace("…", "\n")
                except Exception:
                    continue
            return dec.decode("latin1", errors="ignore").replace("\x85", "\n").replace("…", "\n")
        for enc in ("utf-8", "cp1252", "latin1"):
            try:
                return raw.decode(enc)
            except Exception:
                continue
        return raw.decode("latin1", errors="ignore")

    @staticmethod
    def _fls1_crypt(data: bytes) -> bytes:
        gene = (0x47, 0x65, 0x6E, 0x65)
        out = bytearray()
        for i, b in enumerate(data):
            gene_cipher = ((gene[i % 4] + i) % 256) & 0xFF
            out.append(int(b) ^ (gene_cipher | 0x80))
        return bytes(out)

    def _should_write_fls1(self, path: Path) -> bool:
        try:
            if path.exists() and path.read_bytes().startswith(b"FLS1"):
                return True
        except Exception:
            pass
        # Fallback: if known backups are encrypted, keep encrypted output format.
        backup_candidates = [
            path.with_name(f"{path.name}.FLAtlasBAK"),
            path.with_name(f"{path.name}_BACKUP"),
        ]
        for bp in backup_candidates:
            try:
                if bp.exists() and bp.read_bytes().startswith(b"FLS1"):
                    return True
            except Exception:
                continue
        return False

    def _write_text_preserve_format(self, path: Path, text: str) -> None:
        if self._should_write_fls1(path):
            normalized = str(text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\x85")
            try:
                plain = normalized.encode("cp1252")
            except UnicodeEncodeError:
                plain = normalized.encode("latin1", errors="replace")
            enc = b"FLS1" + self._fls1_crypt(plain)
            path.write_bytes(enc)
            return
        try:
            path.write_text(text, encoding="cp1252")
        except UnicodeEncodeError:
            path.write_text(text, encoding="utf-8")

    def _find_ini_section_bounds(self, lines: list[str], section_name: str, nick: str | None) -> tuple[int, int] | None:
        want = str(section_name or "").strip().lower()
        want_n = str(nick or "").strip().lower() if nick else None
        i = 0
        while i < len(lines):
            t = str(lines[i] or "").strip()
            if t.startswith("[") and t.endswith("]") and t[1:-1].strip().lower() == want:
                j = i + 1
                sec_end = len(lines)
                while j < len(lines):
                    tj = str(lines[j] or "").strip()
                    if tj.startswith("[") and tj.endswith("]"):
                        sec_end = j
                        break
                    j += 1
                if want_n is None:
                    return (i, sec_end)
                found_n = ""
                for k in range(i + 1, sec_end):
                    c = str(lines[k] or "").split(";", 1)[0].strip()
                    if not c or "=" not in c:
                        continue
                    kk, vv = c.split("=", 1)
                    if kk.strip().lower() == "nickname":
                        found_n = vv.strip().lower()
                        break
                if found_n == want_n:
                    return (i, sec_end)
                i = sec_end
                continue
            i += 1
        return None

    def _set_single_key_line_in_section(self, section_lines: list[str], key: str, new_line: str) -> tuple[list[str], bool]:
        if not section_lines:
            return section_lines, False
        out = [section_lines[0]]
        key_l = str(key or "").strip().lower()
        replaced = False
        for ln in section_lines[1:]:
            c = str(ln or "").split(";", 1)[0].strip()
            if c and "=" in c and str(c.split("=", 1)[0] or "").strip().lower() == key_l:
                if not replaced:
                    out.append(new_line)
                    replaced = True
                continue
            out.append(ln)
        if not replaced:
            out.append(new_line)
        return out, True

    def _entry_get_value(self, entries: list[tuple[str, str]], key: str) -> str:
        kl = str(key or "").strip().lower()
        for k, v in entries:
            if str(k or "").strip().lower() == kl:
                return str(v or "").strip()
        return ""

    def _find_all_systems(self, game_path: str) -> list[dict]:
        return find_all_systems(game_path, self._parser, fallback_root=self._fallback_game_path() or None)

    def _freelancer_ini_candidates(self, game_path: str) -> list[Path]:
        out: list[Path] = []
        for rel in ("EXE/freelancer.ini", "freelancer.ini"):
            p = self._resolve_game_path_case_insensitive(game_path, rel)
            if p and p.is_file() and p not in out:
                out.append(p)
        return out

    def _resource_dlls_from_freelancer_ini(self, ini_path: Path) -> list[str]:
        out: list[str] = []
        if not ini_path.exists() or not ini_path.is_file():
            return out
        try:
            sections = self._parser.parse(str(ini_path))
        except Exception:
            return out
        for sec_name, entries in sections:
            if str(sec_name or "").strip().lower() != "resources":
                continue
            for k, v in entries:
                if str(k or "").strip().lower() != "dll":
                    continue
                raw = str(v or "").split(",", 1)[0].strip().strip("\"'")
                if raw and raw not in out:
                    out.append(raw)
        return out

    def _ensure_dll_resolver_loaded(self, game_path: str) -> None:
        gp = str(game_path or "").strip()
        key = self._savegame_editor_cache_key(gp)
        if key == self._dll_lookup_key:
            return
        self._dll_lookup_key = key
        self._dll_resolver.clear()
        if not gp:
            return
        pairs: list[tuple[Path, str]] = []
        for ini_path in self._freelancer_ini_candidates(gp):
            for dll_name in self._resource_dlls_from_freelancer_ini(ini_path):
                pairs.append((ini_path, dll_name))
        if pairs:
            try:
                self._dll_resolver.load_from_resource_pairs(pairs)
            except Exception:
                pass

    def _resolve_ids_name(self, ids_value: str | int | None, game_path: str) -> str:
        txt = str(ids_value or "").strip()
        if not txt:
            return ""
        self._ensure_dll_resolver_loaded(game_path)
        try:
            return str(self._dll_resolver.resolve_name(txt) or "").strip()
        except Exception:
            return ""

    def _system_display_map(self, game_path: str) -> dict[str, str]:
        gp = str(game_path or "").strip()
        if not gp:
            return {}
        cache_key = self._savegame_editor_cache_key(gp)
        if cache_key and cache_key in self._savegame_system_display_cache:
            return dict(self._savegame_system_display_cache.get(cache_key, {}))
        out: dict[str, str] = {}
        try:
            for row in self._find_all_systems(gp):
                nick = str(row.get("nickname", "") or "").strip()
                if not nick:
                    continue
                ids_name = str(row.get("ids_name", "") or row.get("strid_name", "") or "").strip()
                disp = self._resolve_ids_name(ids_name, gp) if ids_name else ""
                out[nick.lower()] = disp or nick
        except Exception:
            pass
        if cache_key:
            self._savegame_system_display_cache[cache_key] = dict(out)
        return out

    def _system_display_name(self, system_nick: str, game_path: str = "") -> str:
        nick = str(system_nick or "").strip()
        if not nick:
            return ""
        if not game_path:
            return nick
        return str(self._system_display_map(game_path).get(nick.lower(), nick) or nick)

    @staticmethod
    def _format_nick_with_display(nick: str, disp: str) -> str:
        n = str(nick or "").strip()
        d = str(disp or "").strip()
        if not n:
            return ""
        if d and d.lower() != n.lower():
            return f"{n} - {d}"
        return n

    def _build_faction_label_cache(self, groups: list[tuple[str, str]], game_path: str = "") -> None:
        self._cached_factions = []
        self._faction_nick_to_label = {}
        self._faction_label_to_nick = {}
        gp = str(game_path or self._primary_game_path() or self._fallback_game_path() or "").strip()
        for nick, _ids in groups:
            n = str(nick or "").strip()
            if not n:
                continue
            disp = self._resolve_ids_name(_ids, gp) if _ids and gp else ""
            label = self._format_nick_with_display(n, disp)
            self._cached_factions.append(n)
            self._faction_nick_to_label[n.lower()] = label
            self._faction_label_to_nick[label.lower()] = n
        self._cached_factions = sorted(set(self._cached_factions), key=str.lower)

    def _faction_ui_label(self, nick: str) -> str:
        n = str(nick or "").strip()
        if not n:
            return ""
        return str(self._faction_nick_to_label.get(n.lower(), n) or n)

    def _faction_from_ui(self, label: str) -> str:
        raw = str(label or "").strip()
        if not raw:
            return ""
        if " - " in raw:
            raw = raw.split(" - ", 1)[0].strip()
        return str(self._faction_label_to_nick.get(raw.lower(), raw) or raw)

    def _fl_hash_table_values(self) -> list[int]:
        if isinstance(self._flhash_table, list) and len(self._flhash_table) == 256:
            return self._flhash_table
        poly = (0xA001 << (30 - 16)) & 0xFFFFFFFF
        table: list[int] = []
        for i in range(256):
            c = i
            for _ in range(8):
                c = ((c >> 1) ^ poly) if (c & 1) else (c >> 1)
            table.append(int(c) & 0xFFFFFFFF)
        self._flhash_table = table
        return table

    def _fl_hash_nickname(self, nickname: str) -> int:
        txt = str(nickname or "").strip().lower()
        if not txt:
            return 0
        table = self._fl_hash_table_values()
        h = 0
        for b in txt.encode("latin1", errors="ignore"):
            h = ((h >> 8) ^ table[(h ^ b) & 0xFF]) & 0xFFFFFFFF
        h = ((h >> 24) | ((h >> 8) & 0x0000FF00) | ((h << 8) & 0x00FF0000) | ((h << 24) & 0xFFFFFFFF)) & 0xFFFFFFFF
        h = ((h >> (32 - 30)) | 0x80000000) & 0xFFFFFFFF
        return int(h)

    def _savegame_editor_load_faction_labels(self, game_path: str = "") -> dict[str, str]:
        groups: list[tuple[str, str]] = []
        roots = [str(game_path or "").strip(), str(self._primary_game_path() or "").strip(), str(self._fallback_game_path() or "").strip()]
        seen_root: set[str] = set()
        for root in roots:
            if not root or root.lower() in seen_root:
                continue
            seen_root.add(root.lower())
            iw_file = self._resolve_game_path_case_insensitive(root, "DATA/initialworld.ini")
            if not iw_file or not iw_file.exists():
                continue
            try:
                for sec_name, entries in self._parser.parse(str(iw_file)):
                    if str(sec_name).strip().lower() != "group":
                        continue
                    nick = self._entry_get_value(entries, "nickname").strip()
                    ids_name = self._entry_get_value(entries, "ids_name").strip()
                    if nick and all(nick.lower() != n.lower() for n, _ in groups):
                        groups.append((nick, ids_name))
            except Exception:
                continue
        groups.sort(key=lambda x: x[0].lower())
        if groups:
            self._build_faction_label_cache(groups, game_path=game_path)
        return {nick.strip().lower(): self._faction_ui_label(nick) for nick in self._cached_factions if nick.strip()}

    def _savegame_editor_collect_rep_templates(self, game_path: str = "") -> list[dict[str, object]]:
        templates: list[dict[str, object]] = []
        roots = [str(game_path or "").strip(), str(self._primary_game_path() or "").strip(), str(self._fallback_game_path() or "").strip()]
        seen_root: set[str] = set()
        rep_by_faction: dict[str, dict[str, float]] = {}
        all_factions: set[str] = set(str(f or "").strip() for f in self._cached_factions if str(f or "").strip())
        for root in roots:
            if not root or root.lower() in seen_root:
                continue
            seen_root.add(root.lower())
            iw_file = self._resolve_game_path_case_insensitive(root, "DATA/initialworld.ini")
            if not iw_file or not iw_file.is_file():
                continue
            try:
                sections = self._parser.parse(str(iw_file))
            except Exception:
                continue
            for sec_name, entries in sections:
                if str(sec_name).strip().lower() != "group":
                    continue
                nick = self._entry_get_value(entries, "nickname").strip()
                if not nick:
                    continue
                all_factions.add(nick)
                houses: dict[str, float] = {}
                for k, v in entries:
                    if str(k or "").strip().lower() != "rep":
                        continue
                    parts = [p.strip() for p in str(v or "").split(",", 1)]
                    if len(parts) < 2:
                        continue
                    try:
                        value = float(parts[0])
                        target = parts[1]
                    except Exception:
                        try:
                            value = float(parts[1])
                            target = parts[0]
                        except Exception:
                            continue
                    target = str(target).strip()
                    if target:
                        houses[target] = float(value)
                        all_factions.add(target)
                if houses:
                    rep_by_faction[nick] = houses
        if all_factions:
            neutral_houses = {fac: 0.0 for fac in sorted(all_factions, key=str.lower)}
            templates.append({"name": "NEUTRAL", "faction": "", "houses": neutral_houses})
        for nick in sorted(rep_by_faction.keys(), key=str.lower):
            label = self._faction_ui_label(nick).strip() or nick
            templates.append({"name": label, "faction": nick, "houses": dict(rep_by_faction.get(nick, {}))})
        return templates

    def _npc_collect_bases(self, game_path: str) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        uni = self._resolve_game_path_case_insensitive(game_path, "DATA/UNIVERSE/universe.ini")
        if not uni or not uni.is_file():
            return out
        try:
            secs = self._parser.parse(str(uni))
        except Exception:
            return out
        for sec_name, entries in secs:
            if str(sec_name).strip().lower() != "base":
                continue
            nick = self._entry_get_value(entries, "nickname").strip()
            sys_nick = self._entry_get_value(entries, "system").strip()
            ids_name = self._entry_get_value(entries, "ids_name").strip() or self._entry_get_value(entries, "strid_name").strip()
            if not nick or not sys_nick:
                continue
            disp = self._resolve_ids_name(ids_name, game_path) if ids_name else ""
            out.append({"nickname": nick, "display": disp or nick, "system": sys_nick, "ids_name": ids_name})
        return out

    def _savegame_editor_collect_nickname_labels(self, game_path: str) -> dict[str, str]:
        labels: dict[str, str] = {}
        gp = str(game_path or "").strip()
        if not gp:
            return labels
        cache_key = self._savegame_editor_cache_key(gp)
        if cache_key and cache_key in self._savegame_nickname_labels_cache:
            return dict(self._savegame_nickname_labels_cache.get(cache_key, {}))

        try:
            for row in self._find_all_systems(gp):
                nick = str(row.get("nickname", "") or "").strip()
                if nick:
                    disp = self._system_display_name(nick, gp)
                    labels[nick.lower()] = self._format_nick_with_display(nick, disp)
        except Exception:
            pass
        try:
            for row in self._npc_collect_bases(gp):
                nick = str(row.get("nickname", "") or "").strip()
                disp = str(row.get("display", "") or "").strip() or nick
                if nick:
                    labels[nick.lower()] = self._format_nick_with_display(nick, disp)
        except Exception:
            pass
        try:
            for sys_row in self._find_all_systems(gp):
                path = str(sys_row.get("path", "") or "").strip()
                if not path:
                    continue
                try:
                    secs = self._parser.parse(path)
                except Exception:
                    continue
                for obj in self._parser.get_objects(secs):
                    nick = str(obj.get("nickname", "") or "").strip()
                    if nick:
                        ids_name = str(obj.get("ids_name", "") or obj.get("strid_name", "") or "").strip()
                        disp = self._resolve_ids_name(ids_name, gp) if ids_name else ""
                        labels[nick.lower()] = self._format_nick_with_display(nick, disp)
        except Exception:
            pass
        for fac in self._cached_factions:
            nick = str(fac or "").strip()
            if nick:
                labels[nick.lower()] = self._faction_ui_label(nick).strip() or nick
        if cache_key:
            self._savegame_nickname_labels_cache[cache_key] = dict(labels)
        return labels

    def _savegame_editor_collect_numeric_id_map(self, game_path: str) -> dict[int, str]:
        out: dict[int, str] = {}
        gp = str(game_path or "").strip()
        if not gp:
            return out
        cache_key = self._savegame_editor_cache_key(gp)
        if cache_key and cache_key in self._savegame_numeric_id_map_cache:
            return dict(self._savegame_numeric_id_map_cache.get(cache_key, {}))
        candidates: set[str] = set()
        try:
            for row in self._find_all_systems(gp):
                nick = str(row.get("nickname", "") or "").strip()
                if nick:
                    candidates.add(nick)
                path = str(row.get("path", "") or "").strip()
                if not path:
                    continue
                try:
                    secs = self._parser.parse(path)
                except Exception:
                    continue
                for obj in self._parser.get_objects(secs):
                    onick = str(obj.get("nickname", "") or "").strip()
                    if onick:
                        candidates.add(onick)
        except Exception:
            pass
        try:
            for row in self._npc_collect_bases(gp):
                nick = str(row.get("nickname", "") or "").strip()
                if nick:
                    candidates.add(nick)
        except Exception:
            pass
        for fac in self._cached_factions:
            nick = str(fac or "").strip()
            if nick:
                candidates.add(nick)
        try:
            item_data = self._savegame_editor_collect_item_data(gp)
            for nick in list(item_data.get("ship_nicks", []) or []):
                n = str(nick or "").strip()
                if n:
                    candidates.add(n)
            for nick in list(item_data.get("equip_nicks", []) or []):
                n = str(nick or "").strip()
                if n:
                    candidates.add(n)
            for nick in list(item_data.get("trent_nicks", []) or []):
                n = str(nick or "").strip()
                if n:
                    candidates.add(n)
        except Exception:
            pass
        for nick in sorted(candidates, key=str.lower):
            hid = int(self._fl_hash_nickname(nick))
            if hid > 0 and hid not in out:
                out[hid] = nick
        if cache_key:
            self._savegame_numeric_id_map_cache[cache_key] = dict(out)
        return out

    def _iter_equipment_ini_paths_for_usage(self, game_path: str) -> list[Path]:
        gp = Path(str(game_path or "").strip())
        if not gp.exists():
            return []
        data_dir = ci_find(gp, "DATA")
        if not data_dir or not data_dir.is_dir():
            return []
        equip_dir = ci_find(data_dir, "EQUIPMENT")
        if not equip_dir or not equip_dir.is_dir():
            return []
        try:
            return sorted(p for p in equip_dir.rglob("*.ini") if p.is_file())
        except Exception:
            return []

    def _iter_character_ini_paths_for_usage(self, game_path: str) -> list[Path]:
        gp = Path(str(game_path or "").strip())
        if not gp.exists():
            return []
        data_dir = ci_find(gp, "DATA")
        if not data_dir or not data_dir.is_dir():
            return []
        char_dir = ci_find(data_dir, "CHARACTERS")
        if not char_dir or not char_dir.is_dir():
            return []
        try:
            return sorted(p for p in char_dir.rglob("*.ini") if p.is_file())
        except Exception:
            return []

    def _sp_starter_equipment_by_type(self, root: Path) -> dict[str, list[str]]:
        by_type: dict[str, set[str]] = {}
        for fp in self._iter_equipment_ini_paths_for_usage(str(root)):
            try:
                sections = self._parser.parse(str(fp))
            except Exception:
                continue
            for sec_name, entries in sections:
                nick = self._entry_get_value(entries, "nickname").strip()
                if not nick:
                    continue
                typ = str(sec_name or "").strip().lower()
                if typ:
                    by_type.setdefault(typ, set()).add(nick)
        return {k: sorted(v, key=str.lower) for k, v in by_type.items()}

    def _sp_starter_item_display_names(self, root: Path) -> dict[str, str]:
        out: dict[str, str] = {}
        shiparch = ci_resolve(root, "DATA/SHIPS/shiparch.ini")
        if shiparch and shiparch.is_file():
            try:
                for sec_name, entries in self._parser.parse(str(shiparch)):
                    if str(sec_name).strip().lower() != "ship":
                        continue
                    nick = self._entry_get_value(entries, "nickname").strip()
                    if nick:
                        ids_name = self._entry_get_value(entries, "ids_name").strip() or self._entry_get_value(entries, "strid_name").strip()
                        disp = self._resolve_ids_name(ids_name, str(root)) if ids_name else ""
                        out.setdefault(nick.lower(), disp or nick)
            except Exception:
                pass
        for fp in self._iter_equipment_ini_paths_for_usage(str(root)):
            try:
                sections = self._parser.parse(str(fp))
            except Exception:
                continue
            for _sec, entries in sections:
                nick = self._entry_get_value(entries, "nickname").strip()
                if nick:
                    ids_name = self._entry_get_value(entries, "ids_name").strip() or self._entry_get_value(entries, "strid_name").strip()
                    disp = self._resolve_ids_name(ids_name, str(root)) if ids_name else ""
                    out.setdefault(nick.lower(), disp or nick)
        for fp in self._iter_character_ini_paths_for_usage(str(root)):
            try:
                sections = self._parser.parse(str(fp))
            except Exception:
                continue
            for _sec, entries in sections:
                nick = self._entry_get_value(entries, "nickname").strip()
                if nick:
                    ids_name = self._entry_get_value(entries, "ids_name").strip() or self._entry_get_value(entries, "strid_name").strip()
                    disp = self._resolve_ids_name(ids_name, str(root)) if ids_name else ""
                    out.setdefault(nick.lower(), disp or nick)
        return out

    def _savegame_editor_collect_item_data(self, game_path: str) -> dict[str, object]:
        gp = str(game_path or "").strip()
        out: dict[str, object] = {
            "item_name_map": {},
            "ship_nicks": [],
            "equip_nicks": [],
            "trent_nicks": [],
            "trent_body_nicks": [],
            "trent_head_nicks": [],
            "trent_lh_nicks": [],
            "trent_rh_nicks": [],
            "ship_hardpoints_by_nick": {},
            "ship_hp_types_by_hardpoint_by_nick": {},
            "equip_type_by_nick": {},
            "equip_hp_types_by_nick": {},
            "hash_to_nick": {},
        }
        if not gp:
            return out
        cache_key = self._savegame_editor_cache_key(gp)
        if cache_key and cache_key in self._savegame_item_data_cache:
            return dict(self._savegame_item_data_cache.get(cache_key, {}))
        root_path = Path(gp)
        if not root_path.exists():
            return out
        item_name_map = self._sp_starter_item_display_names(root_path)
        ship_nicks: list[str] = []
        equip_nicks: list[str] = []
        trent_nicks: list[str] = []
        trent_body_nicks: list[str] = []
        trent_head_nicks: list[str] = []
        trent_lh_nicks: list[str] = []
        trent_rh_nicks: list[str] = []
        ship_hardpoints_by_nick: dict[str, list[str]] = {}
        ship_hp_types_by_hardpoint_by_nick: dict[str, dict[str, list[str]]] = {}
        equip_type_by_nick: dict[str, str] = {}
        equip_hp_types_by_nick: dict[str, list[str]] = {}
        shiparch_ini = ci_resolve(root_path, "DATA/SHIPS/shiparch.ini")
        if shiparch_ini and shiparch_ini.is_file():
            try:
                for sec_name, entries in self._parser.parse(str(shiparch_ini)):
                    if str(sec_name).strip().lower() != "ship":
                        continue
                    nick = self._entry_get_value(entries, "nickname").strip()
                    if not nick:
                        continue
                    ship_nicks.append(nick)
                    hp_seen: set[str] = set()
                    hp_list: list[str] = []
                    hp_type_map_tmp: dict[str, set[str]] = {}
                    for k, v in entries:
                        if str(k).strip().lower() != "hp_type":
                            continue
                        parts = [x.strip() for x in str(v or "").split(",")]
                        if len(parts) < 2:
                            continue
                        hp_type = str(parts[0] or "").strip().lower()
                        for hp_raw in parts[1:]:
                            hp = str(hp_raw or "").strip()
                            if not hp:
                                continue
                            hp_key = hp.lower()
                            if hp_key not in hp_seen:
                                hp_seen.add(hp_key)
                                hp_list.append(hp)
                            if hp_type:
                                hp_type_map_tmp.setdefault(hp_key, set()).add(hp_type)
                    ship_hardpoints_by_nick[nick.lower()] = hp_list
                    if hp_type_map_tmp:
                        ship_hp_types_by_hardpoint_by_nick[nick.lower()] = {
                            hk: sorted(hv, key=str.lower) for hk, hv in hp_type_map_tmp.items() if hv
                        }
            except Exception:
                pass
        try:
            by_type = self._sp_starter_equipment_by_type(root_path)
            seen_equ: set[str] = set()
            for sec_type, vals in by_type.items():
                for nick in vals:
                    key = str(nick).strip().lower()
                    if key and key not in seen_equ:
                        seen_equ.add(key)
                        equip_nicks.append(str(nick).strip())
                    if key and key not in equip_type_by_nick:
                        equip_type_by_nick[key] = str(sec_type or "").strip().lower()
            hp_tmp: dict[str, set[str]] = {}
            for fp in self._iter_equipment_ini_paths_for_usage(str(root_path)):
                try:
                    sections = self._parser.parse(str(fp))
                except Exception:
                    continue
                for _sec_name, entries in sections:
                    nick = self._entry_get_value(entries, "nickname").strip()
                    if not nick:
                        continue
                    key = nick.lower()
                    hp_set = hp_tmp.setdefault(key, set())
                    for k, v in entries:
                        if str(k or "").strip().lower() != "hp_type":
                            continue
                        parts = [x.strip() for x in str(v or "").split(",")]
                        for part in parts:
                            hp = str(part or "").strip().lower()
                            if hp:
                                hp_set.add(hp)
            equip_hp_types_by_nick = {k: sorted(v, key=str.lower) for k, v in hp_tmp.items() if v}
        except Exception:
            pass
        try:
            seen_trent: set[str] = set()
            seen_body: set[str] = set()
            seen_head: set[str] = set()
            seen_lh: set[str] = set()
            seen_rh: set[str] = set()
            for fp in self._iter_character_ini_paths_for_usage(str(root_path)):
                try:
                    sections = self._parser.parse(str(fp))
                except Exception:
                    continue
                for sec_name, entries in sections:
                    nick = self._entry_get_value(entries, "nickname").strip()
                    if not nick:
                        continue
                    key = nick.lower()
                    if key in seen_trent:
                        continue
                    seen_trent.add(key)
                    trent_nicks.append(nick)
                    sec = str(sec_name or "").strip().lower()
                    if sec == "body":
                        if key not in seen_body:
                            seen_body.add(key)
                            trent_body_nicks.append(nick)
                    elif sec == "head":
                        if key not in seen_head:
                            seen_head.add(key)
                            trent_head_nicks.append(nick)
                    elif sec in {"lefthand", "left_hand"}:
                        if key not in seen_lh:
                            seen_lh.add(key)
                            trent_lh_nicks.append(nick)
                    elif sec in {"righthand", "right_hand"}:
                        if key not in seen_rh:
                            seen_rh.add(key)
                            trent_rh_nicks.append(nick)
        except Exception:
            pass
        hash_to_nick: dict[int, str] = {}
        nicks_for_hash: set[str] = set()
        nicks_for_hash.update(str(n).strip() for n in ship_nicks if str(n).strip())
        nicks_for_hash.update(str(n).strip() for n in equip_nicks if str(n).strip())
        nicks_for_hash.update(str(n).strip() for n in trent_nicks if str(n).strip())
        nicks_for_hash.update(str(k).strip() for k in item_name_map.keys() if str(k).strip())
        for nick in nicks_for_hash:
            hid = self._fl_hash_nickname(nick)
            if hid > 0 and hid not in hash_to_nick:
                hash_to_nick[hid] = nick
        out = {
            "item_name_map": dict(item_name_map),
            "ship_nicks": sorted(set(ship_nicks), key=str.lower),
            "equip_nicks": sorted(set(equip_nicks), key=str.lower),
            "trent_nicks": sorted(set(trent_nicks), key=str.lower),
            "trent_body_nicks": sorted(set(trent_body_nicks), key=str.lower),
            "trent_head_nicks": sorted(set(trent_head_nicks), key=str.lower),
            "trent_lh_nicks": sorted(set(trent_lh_nicks), key=str.lower),
            "trent_rh_nicks": sorted(set(trent_rh_nicks), key=str.lower),
            "ship_hardpoints_by_nick": dict(ship_hardpoints_by_nick),
            "ship_hp_types_by_hardpoint_by_nick": dict(ship_hp_types_by_hardpoint_by_nick),
            "equip_type_by_nick": dict(equip_type_by_nick),
            "equip_hp_types_by_nick": dict(equip_hp_types_by_nick),
            "hash_to_nick": dict(hash_to_nick),
        }
        if cache_key:
            self._savegame_item_data_cache[cache_key] = dict(out)
        return out

    def _savegame_editor_collect_jump_connections(self, game_path: str) -> dict[str, object]:
        gp = str(game_path or "").strip()
        out: dict[str, object] = {"systems": {}, "edges": [], "all_gate_ids": set()}
        if not gp:
            return out
        cache_key = self._savegame_editor_cache_key(gp)
        if cache_key and cache_key in self._savegame_jump_connections_cache:
            cached = self._savegame_jump_connections_cache.get(cache_key, {})
            return {
                "systems": dict(cached.get("systems", {}) or {}),
                "edges": list(cached.get("edges", []) or []),
                "all_gate_ids": set(cached.get("all_gate_ids", set()) or set()),
            }
        systems = list(self._find_all_systems(gp))
        sys_map: dict[str, dict[str, object]] = {}
        for row in systems:
            sn = str(row.get("nickname", "") or "").strip()
            if not sn:
                continue
            sx, sy = row.get("pos", (0.0, 0.0))
            sys_map[sn.upper()] = {
                "nickname": sn,
                "display": self._system_display_name(sn, gp).strip() or sn,
                "x": float(sx or 0.0),
                "y": float(sy or 0.0),
            }
        edges_map: dict[frozenset[str], dict[str, object]] = {}
        all_gate_ids: set[int] = set()
        for row in systems:
            src = str(row.get("nickname", "") or "").strip().upper()
            path = str(row.get("path", "") or "").strip()
            if not src or not path:
                continue
            try:
                secs = self._parser.parse(path)
            except Exception:
                continue
            for obj in self._parser.get_objects(secs):
                arch = str(obj.get("archetype", "") or "").strip().lower()
                if "jumpgate" in arch or "nomad_gate" in arch:
                    typ = "gate"
                elif "jumphole" in arch or "jump_hole" in arch:
                    typ = "hole"
                else:
                    continue
                goto_raw = str(obj.get("goto", "") or "").strip()
                dest = goto_raw.split(",", 1)[0].strip().upper() if goto_raw else ""
                if not dest or dest == src:
                    continue
                obj_nick = str(obj.get("nickname", "") or "").strip()
                obj_id = self._fl_hash_nickname(obj_nick) if obj_nick else 0
                if obj_id > 0:
                    all_gate_ids.add(int(obj_id))
                key = frozenset({src, dest})
                edge = edges_map.get(key)
                if edge is None:
                    edge = {"a": src, "b": dest, "type": typ, "ids": set(), "nicks": set()}
                    edges_map[key] = edge
                elif str(edge.get("type", "")).lower() == "hole" and typ == "gate":
                    edge["type"] = "gate"
                if obj_id > 0:
                    ids_set = edge.get("ids")
                    if isinstance(ids_set, set):
                        ids_set.add(int(obj_id))
                if obj_nick:
                    nicks_set = edge.get("nicks")
                    if isinstance(nicks_set, set):
                        nicks_set.add(obj_nick)
        edges_out: list[dict[str, object]] = []
        for key, row in edges_map.items():
            a, b = list(key)
            edges_out.append(
                {
                    "a": a,
                    "b": b,
                    "type": str(row.get("type", "hole") or "hole"),
                    "ids": sorted(int(v) for v in (row.get("ids") or set()) if int(v) > 0),
                    "nicks": sorted(str(v) for v in (row.get("nicks") or set()) if str(v)),
                }
            )
        out = {"systems": sys_map, "edges": edges_out, "all_gate_ids": set(all_gate_ids)}
        if cache_key:
            self._savegame_jump_connections_cache[cache_key] = {
                "systems": dict(sys_map),
                "edges": list(edges_out),
                "all_gate_ids": set(all_gate_ids),
            }
        return out


def open_savegame_editor(self):
    default_dir = self._default_savegame_editor_dir()
    default_game_path = self._default_savegame_editor_game_path()
    game_path = str(default_game_path or self._primary_game_path() or self._fallback_game_path() or "").strip()
    faction_labels = self._savegame_editor_load_faction_labels(game_path)
    templates = self._savegame_editor_collect_rep_templates(game_path)
    nickname_labels = self._savegame_editor_collect_nickname_labels(game_path)
    numeric_id_map = self._savegame_editor_collect_numeric_id_map(game_path)
    system_label_by_nick: dict[str, str] = {}
    system_to_bases: dict[str, list[dict[str, str]]] = {}
    if game_path:
        try:
            for row in self._npc_collect_bases(game_path):
                base_nick = str(row.get("nickname", "")).strip()
                base_disp = str(row.get("display", "")).strip() or base_nick
                sys_nick = str(row.get("system", "")).strip()
                if not base_nick or not sys_nick:
                    continue
                sys_name = self._system_display_name(sys_nick, game_path).strip() or sys_nick
                sys_label = f"{sys_nick} - {sys_name}" if sys_name.lower() != sys_nick.lower() else sys_nick
                system_label_by_nick[sys_nick] = sys_label
                system_to_bases.setdefault(sys_nick, []).append({"nickname": base_nick, "display": base_disp})
        except Exception:
            system_label_by_nick = {}
            system_to_bases = {}
    for sys_nick, rows in system_to_bases.items():
        rows.sort(key=lambda r: str(r.get("display", "")).lower())

    dlg = QDialog(self)
    try:
        dlg.setWindowIcon(self.windowIcon())
    except Exception:
        pass
    dlg.resize(1120, 800)
    lay = QVBoxLayout(dlg)
    lay.setContentsMargins(10, 10, 10, 10)
    lay.setSpacing(8)
    menu_bar = QMenuBar(dlg)
    menu_bar.setNativeMenuBar(False)
    lay.setMenuBar(menu_bar)
    file_menu = menu_bar.addMenu(tr("savegame_editor.menu.file"))
    settings_menu = menu_bar.addMenu(tr("savegame_editor.menu.settings"))
    help_menu = menu_bar.addMenu(tr("savegame_editor.menu.help"))
    language_menu = menu_bar.addMenu(_tr_or("savegame_editor.menu.language", "Language"))
    theme_menu = settings_menu.addMenu(_tr_or("savegame_editor.menu.theme", "Theme"))

    def _set_editor_title(path: Path | None = None) -> None:
        base = f"{tr('savegame_editor.title')} {SAVEGAME_EDITOR_VERSION}"
        if isinstance(path, Path):
            dlg.setWindowTitle(f"{base} -> {path.name}")
        else:
            dlg.setWindowTitle(base)

    _set_editor_title(None)

    save_dir_edit = QLineEdit(str(default_dir))
    game_path_edit = QLineEdit(game_path)

    savegame_cb = QComboBox(dlg)
    savegame_cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    savegame_cb.setMinimumWidth(360)
    save_sel_host = QWidget(dlg)
    save_sel_l = QHBoxLayout(save_sel_host)
    save_sel_l.setContentsMargins(0, 0, 0, 0)
    save_sel_l.setSpacing(6)
    save_sel_l.addWidget(QLabel(tr("savegame_editor.select"), save_sel_host))
    save_sel_l.addWidget(savegame_cb, 1)
    menu_bar.setCornerWidget(save_sel_host, Qt.TopRightCorner)

    info_lbl = QLabel("")
    info_lbl.setWordWrap(True)
    lay.addWidget(info_lbl)
    load_progress = QProgressBar(dlg)
    load_progress.setVisible(False)
    lay.addWidget(load_progress)

    content_row = QHBoxLayout()
    content_row.setContentsMargins(0, 0, 0, 0)
    content_row.setSpacing(10)
    sidebar = QWidget(dlg)
    sidebar.setMinimumWidth(320)
    sidebar.setMaximumWidth(380)
    sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
    sidebar_l = QVBoxLayout(sidebar)
    sidebar_l.setContentsMargins(0, 0, 0, 0)
    sidebar_l.setSpacing(8)
    right_tabs = QTabWidget(dlg)
    tab_locked = QWidget(dlg)
    tab_visited = QWidget(dlg)
    tab_reputation = QWidget(dlg)
    tab_trent = QWidget(dlg)
    tab_ship = QWidget(dlg)
    rep_l = QVBoxLayout(tab_reputation)
    rep_l.setContentsMargins(8, 8, 8, 8)
    rep_l.setSpacing(8)
    trent_l = QVBoxLayout(tab_trent)
    trent_l.setContentsMargins(8, 8, 8, 8)
    trent_l.setSpacing(8)
    ship_tab_l = QVBoxLayout(tab_ship)
    ship_tab_l.setContentsMargins(8, 8, 8, 8)
    ship_tab_l.setSpacing(8)
    right_tabs.addTab(tab_locked, tr("savegame_editor.map_tab.locked"))
    right_tabs.addTab(tab_visited, tr("savegame_editor.map_tab.visited"))
    right_tabs.addTab(tab_reputation, tr("savegame_editor.tab.reputation"))
    right_tabs.addTab(tab_trent, tr("savegame_editor.tab.trent"))
    right_tabs.addTab(tab_ship, tr("savegame_editor.tab.ship"))
    content_row.addWidget(sidebar, 0)
    content_row.addWidget(right_tabs, 1)
    content_row.setStretch(0, 0)
    content_row.setStretch(1, 1)
    lay.addLayout(content_row, 1)

    form = QFormLayout()
    rank_spin = QSpinBox(dlg)
    rank_spin.setRange(0, 100)
    money_spin = QSpinBox(dlg)
    money_spin.setRange(0, 999_999_999)
    description_edit = QLineEdit(dlg)
    rep_group_cb = QComboBox(dlg)
    rep_group_cb.setEditable(True)
    rep_group_cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    rep_group_cb.setMinimumContentsLength(20)
    for nick in sorted(self._cached_factions, key=str.lower):
        label = faction_labels.get(str(nick).strip().lower(), self._faction_ui_label(nick) or str(nick))
        rep_group_cb.addItem(label, str(nick))
    system_cb = QComboBox(dlg)
    system_cb.setEditable(True)
    system_cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    system_cb.setMinimumContentsLength(20)
    for sys_nick in sorted(system_to_bases.keys(), key=lambda s: str(system_label_by_nick.get(s, s)).lower()):
        system_cb.addItem(system_label_by_nick.get(sys_nick, sys_nick), sys_nick)
    base_cb = QComboBox(dlg)
    base_cb.setEditable(True)
    base_cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    base_cb.setMinimumContentsLength(20)
    sidebar_field_width = 280
    for w in (rank_spin, money_spin, description_edit, rep_group_cb, system_cb, base_cb):
        w.setMinimumWidth(sidebar_field_width)
        w.setMaximumWidth(sidebar_field_width)
    form.addRow(tr("savegame_editor.rank"), rank_spin)
    form.addRow(tr("savegame_editor.money"), money_spin)
    form.addRow(tr("savegame_editor.description"), description_edit)
    form.addRow(tr("savegame_editor.rep_group"), rep_group_cb)
    form.addRow(tr("savegame_editor.system"), system_cb)
    form.addRow(tr("savegame_editor.base"), base_cb)
    story_lock_lbl = QLabel("", dlg)
    story_lock_lbl.setWordWrap(True)
    story_lock_lbl.setVisible(False)
    story_lock_lbl.setStyleSheet("color: #9aa0a6;")
    form.addRow("", story_lock_lbl)
    sidebar_l.addLayout(form)
    validate_btn = QPushButton(tr("savegame_editor.validate"), dlg)
    sidebar_l.addWidget(validate_btn)
    validate_help_lbl = QLabel(tr("savegame_editor.validate_help"), dlg)
    validate_help_lbl.setWordWrap(True)
    validate_help_lbl.setStyleSheet("color: #9aa0a6;")
    sidebar_l.addWidget(validate_help_lbl)
    sidebar_l.addStretch(1)

    locked_map_l = QVBoxLayout(tab_locked)
    locked_map_l.setContentsMargins(0, 0, 0, 0)
    locked_map_l.setSpacing(6)
    locked_scene = QGraphicsScene(tab_locked)
    locked_view = _SavegameKnownMapView(locked_scene, tab_locked)
    locked_view.setRenderHint(QPainter.Antialiasing, True)
    locked_view.setMinimumHeight(240)
    locked_view.setStyleSheet("QGraphicsView { border: 1px solid palette(mid); }")
    locked_map_l.addWidget(locked_view, 1)
    unlock_all_btn = QPushButton(tr("savegame_editor.unlock_all"), tab_locked)
    locked_map_l.addWidget(unlock_all_btn, 0, Qt.AlignRight)
    visited_map_l = QVBoxLayout(tab_visited)
    visited_map_l.setContentsMargins(0, 0, 0, 0)
    visited_map_l.setSpacing(6)
    visited_scene = QGraphicsScene(tab_visited)
    visited_view = _SavegameKnownMapView(visited_scene, tab_visited)
    visited_view.setRenderHint(QPainter.Antialiasing, True)
    visited_view.setMinimumHeight(240)
    visited_view.setStyleSheet("QGraphicsView { border: 1px solid palette(mid); }")
    visited_map_l.addWidget(visited_view, 1)
    visit_unlock_all_btn = QPushButton(tr("savegame_editor.visit_unlock_all"), tab_visited)
    visited_map_l.addWidget(visit_unlock_all_btn, 0, Qt.AlignRight)

    def _map_colors_for_theme(theme_name: str) -> dict[str, QColor]:
        t = str(theme_name or "Standard").strip()
        if t == "Light":
            return {
                "bg": QColor("#f6f8fc"),
                "line_inactive": QColor("#9aa6b2"),
                "line_locked": QColor("#d64545"),
                "line_visited": QColor("#2b6ed2"),
                "node_inactive": QColor("#8c99a8"),
                "node_locked": QColor("#d64545"),
                "node_visited": QColor("#2f9e44"),
                "node_outline": QColor("#5f6b7a"),
                "text_inactive": QColor("#425166"),
                "text_locked": QColor("#7f1d1d"),
                "text_visited": QColor("#1f2937"),
                "text_empty": QColor("#5b6778"),
            }
        if t == "High Contrast":
            return {
                "bg": QColor("#000000"),
                "line_inactive": QColor("#8f8f8f"),
                "line_locked": QColor("#ff3333"),
                "line_visited": QColor("#00a6ff"),
                "node_inactive": QColor("#9f9f9f"),
                "node_locked": QColor("#ff3333"),
                "node_visited": QColor("#00ff66"),
                "node_outline": QColor("#ffffff"),
                "text_inactive": QColor("#d7d7d7"),
                "text_locked": QColor("#ff9999"),
                "text_visited": QColor("#ffffff"),
                "text_empty": QColor("#ffffff"),
            }
        return {
            "bg": QColor("#0f141d"),
            "line_inactive": QColor("#8a8a8a"),
            "line_locked": QColor("#d33f49"),
            "line_visited": QColor("#3c82dc"),
            "node_inactive": QColor("#9aa0a6"),
            "node_locked": QColor("#d33f49"),
            "node_visited": QColor("#2f9e44"),
            "node_outline": QColor("#202020"),
            "text_inactive": QColor("#a7a7a7"),
            "text_locked": QColor("#ffd5d8"),
            "text_visited": QColor("#d8d8d8"),
            "text_empty": QColor("#a7a7a7"),
        }

    map_colors: dict[str, QColor] = _map_colors_for_theme(self._cfg.get("settings.theme", "Standard"))

    def _apply_map_theme(theme_name: str) -> None:
        nonlocal map_colors
        map_colors = _map_colors_for_theme(theme_name)
        locked_scene.setBackgroundBrush(QBrush(map_colors["bg"]))
        visited_scene.setBackgroundBrush(QBrush(map_colors["bg"]))

    _apply_map_theme(self._cfg.get("settings.theme", "Standard"))

    tpl_row = QHBoxLayout()
    tpl_row.addWidget(QLabel(tr("savegame_editor.template")))
    template_cb = QComboBox(dlg)
    for tpl in templates:
        template_cb.addItem(str(tpl.get("name") or ""), tpl)
    template_cb.setEnabled(bool(templates))
    template_cb.setCurrentIndex(-1)
    tpl_row.addWidget(template_cb, 1)
    apply_template_btn = QPushButton(tr("savegame_editor.template_apply"), dlg)
    apply_template_btn.setEnabled(bool(templates))
    tpl_row.addWidget(apply_template_btn)
    rep_l.addLayout(tpl_row)

    item_data = self._savegame_editor_collect_item_data(game_path)
    item_name_map: dict[str, str] = dict(item_data.get("item_name_map", {}) or {})
    ship_nicks: list[str] = list(item_data.get("ship_nicks", []) or [])
    equip_nicks: list[str] = list(item_data.get("equip_nicks", []) or [])
    trent_nicks: list[str] = list(item_data.get("trent_nicks", []) or [])
    trent_body_nicks: list[str] = list(item_data.get("trent_body_nicks", []) or [])
    trent_head_nicks: list[str] = list(item_data.get("trent_head_nicks", []) or [])
    trent_lh_nicks: list[str] = list(item_data.get("trent_lh_nicks", []) or [])
    trent_rh_nicks: list[str] = list(item_data.get("trent_rh_nicks", []) or [])
    ship_hardpoints_by_nick: dict[str, list[str]] = {
        str(k): list(v) for k, v in dict(item_data.get("ship_hardpoints_by_nick", {}) or {}).items()
    }
    ship_hp_types_by_hardpoint_by_nick: dict[str, dict[str, list[str]]] = {
        str(k): {str(hk): list(hv) for hk, hv in dict(hmap).items()}
        for k, hmap in dict(item_data.get("ship_hp_types_by_hardpoint_by_nick", {}) or {}).items()
    }
    equip_type_by_nick: dict[str, str] = {
        str(k): str(v) for k, v in dict(item_data.get("equip_type_by_nick", {}) or {}).items()
    }
    equip_hp_types_by_nick: dict[str, list[str]] = {
        str(k): list(v) for k, v in dict(item_data.get("equip_hp_types_by_nick", {}) or {}).items()
    }
    hash_to_nick: dict[int, str] = {int(k): str(v) for k, v in dict(item_data.get("hash_to_nick", {}) or {}).items()}
    jump_data = self._savegame_editor_collect_jump_connections(game_path)

    trent_form = QFormLayout()
    com_body_cb = QComboBox(dlg)
    com_head_cb = QComboBox(dlg)
    com_lh_cb = QComboBox(dlg)
    com_rh_cb = QComboBox(dlg)
    body_cb = QComboBox(dlg)
    head_cb = QComboBox(dlg)
    lh_cb = QComboBox(dlg)
    rh_cb = QComboBox(dlg)
    trent_item_cbs = [com_body_cb, com_head_cb, com_lh_cb, com_rh_cb, body_cb, head_cb, lh_cb, rh_cb]
    for cb in trent_item_cbs:
        cb.setEditable(True)
    trent_form.addRow(tr("savegame_editor.trent.com_body"), com_body_cb)
    trent_form.addRow(tr("savegame_editor.trent.com_head"), com_head_cb)
    trent_form.addRow(tr("savegame_editor.trent.com_lh"), com_lh_cb)
    trent_form.addRow(tr("savegame_editor.trent.com_rh"), com_rh_cb)
    trent_form.addRow(tr("savegame_editor.trent.body"), body_cb)
    trent_form.addRow(tr("savegame_editor.trent.head"), head_cb)
    trent_form.addRow(tr("savegame_editor.trent.lh"), lh_cb)
    trent_form.addRow(tr("savegame_editor.trent.rh"), rh_cb)
    trent_l.addLayout(trent_form)
    trent_l.addStretch(1)

    ship_box = QGroupBox(tr("savegame_editor.ship_group"), dlg)
    ship_l = QVBoxLayout(ship_box)
    ship_l.setContentsMargins(8, 8, 8, 8)
    ship_l.setSpacing(6)
    ship_form = QFormLayout()
    ship_archetype_cb = QComboBox(dlg)
    ship_archetype_cb.setEditable(True)
    ship_form.addRow(tr("savegame_editor.ship_archetype"), ship_archetype_cb)
    ship_l.addLayout(ship_form)
    hardpoint_hint_lbl = QLabel("", dlg)
    hardpoint_hint_lbl.setWordWrap(True)
    ship_l.addWidget(hardpoint_hint_lbl)

    equip_lbl = QLabel(tr("savegame_editor.equip"), dlg)
    ship_l.addWidget(equip_lbl)
    equip_tbl = QTableWidget(0, 2, dlg)
    equip_tbl.setHorizontalHeaderLabels([tr("savegame_editor.col.item"), tr("savegame_editor.col.hardpoint")])
    eh = equip_tbl.horizontalHeader()
    eh.setSectionResizeMode(0, QHeaderView.Stretch)
    eh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    equip_tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
    equip_tbl.setSelectionMode(QAbstractItemView.SingleSelection)
    equip_tbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    ship_l.addWidget(equip_tbl, 1)
    equip_btn_row = QHBoxLayout()
    equip_add_btn = QPushButton(tr("savegame_editor.btn.add_equip"), dlg)
    equip_del_btn = QPushButton(tr("savegame_editor.btn.remove_selected"), dlg)
    equip_autofix_btn = QPushButton(tr("savegame_editor.btn.autofix_hardpoints"), dlg)
    equip_btn_row.addWidget(equip_add_btn)
    equip_btn_row.addWidget(equip_del_btn)
    equip_btn_row.addWidget(equip_autofix_btn)
    equip_btn_row.addStretch(1)
    ship_l.addLayout(equip_btn_row)

    cargo_lbl = QLabel(tr("savegame_editor.cargo"), dlg)
    ship_l.addWidget(cargo_lbl)
    cargo_tbl = QTableWidget(0, 2, dlg)
    cargo_tbl.setHorizontalHeaderLabels([tr("savegame_editor.col.item"), tr("savegame_editor.col.amount")])
    ch = cargo_tbl.horizontalHeader()
    ch.setSectionResizeMode(0, QHeaderView.Stretch)
    ch.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    cargo_tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
    cargo_tbl.setSelectionMode(QAbstractItemView.SingleSelection)
    cargo_tbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    ship_l.addWidget(cargo_tbl, 1)
    cargo_btn_row = QHBoxLayout()
    cargo_add_btn = QPushButton(tr("savegame_editor.btn.add_cargo"), dlg)
    cargo_del_btn = QPushButton(tr("savegame_editor.btn.remove_selected"), dlg)
    cargo_btn_row.addWidget(cargo_add_btn)
    cargo_btn_row.addWidget(cargo_del_btn)
    cargo_btn_row.addStretch(1)
    ship_l.addLayout(cargo_btn_row)
    ship_tab_l.addWidget(ship_box, 1)

    houses_lbl = QLabel(tr("savegame_editor.houses"))
    rep_l.addWidget(houses_lbl)
    houses_tbl = QTableWidget(0, 3, dlg)
    houses_tbl.setHorizontalHeaderLabels(
        [tr("savegame_editor.col.faction"), tr("savegame_editor.col.rep"), tr("savegame_editor.col.slider")]
    )
    hh = houses_tbl.horizontalHeader()
    hh.setSectionResizeMode(0, QHeaderView.Stretch)
    hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
    hh.setSectionResizeMode(2, QHeaderView.Stretch)
    houses_tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
    houses_tbl.setSelectionMode(QAbstractItemView.SingleSelection)
    rep_l.addWidget(houses_tbl, 1)

    bottom_row = QHBoxLayout()
    bottom_row.addStretch(1)
    save_btn = QPushButton(tr("savegame_editor.save"), dlg)
    close_btn = QPushButton(tr("dlg.close"), dlg)
    bottom_row.addWidget(save_btn)
    bottom_row.addWidget(close_btn)
    lay.addLayout(bottom_row)
    footer = QLabel(
        tr("savegame_editor.footer_html").format(
            version=SAVEGAME_EDITOR_VERSION,
            discord=DISCORD_INVITE_URL,
            bugs=BUG_REPORT_URL,
        ),
        dlg,
    )
    footer.setOpenExternalLinks(True)
    footer.setTextFormat(Qt.RichText)
    footer.setWordWrap(True)
    footer.setTextInteractionFlags(Qt.TextBrowserInteraction)
    footer.setStyleSheet("color: #9aa0a6; padding-top: 2px;")
    lay.addWidget(footer)

    state: dict[str, object] = {
        "path": None,
        "updating_savegame_cb": False,
        "locked_ids": set(),
        "visit_ids": set(),
        "visit_line_by_id": {},
        "story_locked": False,
    }
    map_state: dict[str, object] = {"locked_ids": set(), "visit_ids": set()}

    def _clear_maps() -> None:
        locked_scene.clear()
        visited_scene.clear()
        empty = QRectF(0, 0, 1, 1)
        locked_scene.setSceneRect(empty)
        visited_scene.setSceneRect(empty)
        locked_view.set_base_rect(empty)
        visited_view.set_base_rect(empty)
        map_state["locked_ids"] = set()
        map_state["visit_ids"] = set()

    def _set_no_savegame_state() -> None:
        state["path"] = None
        state["locked_ids"] = set()
        state["visit_ids"] = set()
        state["visit_line_by_id"] = {}
        rank_spin.setValue(0)
        money_spin.setValue(0)
        description_edit.clear()
        rep_group_cb.setCurrentIndex(-1)
        rep_group_cb.setEditText("")
        system_cb.setCurrentIndex(-1)
        system_cb.setEditText("")
        base_cb.clear()
        for cb in trent_item_cbs:
            cb.setCurrentIndex(-1)
            cb.setEditText("")
        ship_archetype_cb.setCurrentIndex(-1)
        ship_archetype_cb.setEditText("")
        equip_tbl.setRowCount(0)
        cargo_tbl.setRowCount(0)
        houses_tbl.setRowCount(0)
        _set_story_lock_ui(False, 0)
        _clear_maps()
        for w in (
            rank_spin,
            money_spin,
            description_edit,
            rep_group_cb,
            system_cb,
            base_cb,
            com_body_cb,
            com_head_cb,
            com_lh_cb,
            com_rh_cb,
            body_cb,
            head_cb,
            lh_cb,
            rh_cb,
            ship_archetype_cb,
            equip_tbl,
            cargo_tbl,
            houses_tbl,
            template_cb,
            apply_template_btn,
            unlock_all_btn,
            visit_unlock_all_btn,
            equip_add_btn,
            equip_del_btn,
            equip_autofix_btn,
            cargo_add_btn,
            cargo_del_btn,
            right_tabs,
            validate_btn,
            validate_help_lbl,
        ):
            w.setEnabled(False)
        act_file_reload.setEnabled(False)
        act_file_save.setEnabled(False)

    def _set_savegame_loaded_state() -> None:
        for w in (
            rank_spin,
            money_spin,
            description_edit,
            rep_group_cb,
            system_cb,
            base_cb,
            com_body_cb,
            com_head_cb,
            com_lh_cb,
            com_rh_cb,
            body_cb,
            head_cb,
            lh_cb,
            rh_cb,
            ship_archetype_cb,
            equip_tbl,
            cargo_tbl,
            houses_tbl,
            template_cb,
            apply_template_btn,
            unlock_all_btn,
            visit_unlock_all_btn,
            equip_add_btn,
            equip_del_btn,
            equip_autofix_btn,
            cargo_add_btn,
            cargo_del_btn,
            right_tabs,
            validate_btn,
            validate_help_lbl,
        ):
            w.setEnabled(True)
        template_cb.setEnabled(bool(templates))
        apply_template_btn.setEnabled(bool(templates))
        act_file_reload.setEnabled(True)
        act_file_save.setEnabled(True)

    def _set_loading(active: bool) -> None:
        load_progress.setVisible(active)
        if active:
            load_progress.setRange(0, 0)
            load_progress.setFormat(tr("savegame_editor.loading"))
        else:
            load_progress.setRange(0, 1)
            load_progress.setValue(0)
        QApplication.processEvents()

    def _save_dir() -> Path:
        txt = save_dir_edit.text().strip()
        if txt:
            return self._canonical_savegame_dir_from_input(txt)
        return default_dir

    def _token_to_known_nick(token: str) -> str:
        raw = str(token or "").strip()
        if not raw:
            return ""
        if raw.isdigit():
            try:
                hid = int(raw)
            except Exception:
                hid = 0
            if hid > 0:
                mapped = str(hash_to_nick.get(hid, "") or "").strip()
                if mapped:
                    return mapped
                mapped2 = str(numeric_id_map.get(hid, "") or "").strip()
                if mapped2:
                    return mapped2
        return raw

    def _validate_savegame() -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.no_file"))
            return
        fixed_hardpoints = _autofix_invalid_hardpoints(show_result=False)
        try:
            raw = self._read_text_best_effort(cur)
        except Exception as exc:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), str(exc))
            return
        lines = raw.splitlines()
        bounds = self._find_ini_section_bounds(lines, "Player", None)
        if bounds is None:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), tr("savegame_editor.validate.player_missing"))
            return
        s, e = bounds
        player_lines = lines[s:e]

        known_ships = {str(v).strip().lower() for v in ship_nicks if str(v).strip()}
        known_equip = {str(v).strip().lower() for v in equip_nicks if str(v).strip()}
        known_factions = {str(v).strip().lower() for v in self._cached_factions if str(v).strip()}
        known_systems = {str(v).strip().upper() for v in system_to_bases.keys() if str(v).strip()}
        known_bases = {
            str(row.get("nickname", "")).strip().upper()
            for rows in system_to_bases.values()
            for row in list(rows or [])
            if str(row.get("nickname", "")).strip()
        }
        known_visit_ids = {int(k) for k in numeric_id_map.keys() if int(k) > 0}
        known_nicks_generic = {str(v).strip().lower() for v in numeric_id_map.values() if str(v).strip()}

        issues: list[str] = []
        suggestions: list[str] = []
        bad_ships: set[str] = set()
        bad_equip: set[str] = set()
        bad_cargo: set[str] = set()
        bad_factions: set[str] = set()
        bad_visit: set[str] = set()
        bad_systems: set[str] = set()
        bad_bases: set[str] = set()
        skipped_visit_unknown_numeric = 0

        for raw_line in player_lines[1:]:
            line = str(raw_line).strip()
            if not line or line.startswith(";") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            k = key.strip().lower()
            v = val.strip()
            if k == "ship_archetype":
                nick = _token_to_known_nick(v).strip()
                if nick and nick.lower() not in known_ships:
                    bad_ships.add(v.strip())
            elif k == "equip":
                parts = [x.strip() for x in v.split(",")]
                item_tok = parts[0] if parts else ""
                nick = _token_to_known_nick(item_tok).strip()
                if nick and nick.lower() not in known_equip:
                    bad_equip.add(item_tok)
            elif k == "cargo":
                parts = [x.strip() for x in v.split(",")]
                item_tok = parts[0] if parts else ""
                nick = _token_to_known_nick(item_tok).strip()
                if nick and nick.lower() not in known_equip:
                    bad_cargo.add(item_tok)
            elif k == "rep_group":
                fac = str(v or "").strip()
                fac_nick = self._faction_from_ui(fac) or fac
                if fac_nick and fac_nick.lower() not in known_factions:
                    bad_factions.add(fac)
            elif k == "house":
                parts = [x.strip() for x in v.split(",", 1)]
                if len(parts) >= 2:
                    fac = str(parts[1] or "").strip()
                    if fac and fac.lower() not in known_factions:
                        bad_factions.add(fac)
            elif k == "visit":
                parts = [x.strip() for x in v.split(",", 1)]
                tok = parts[0] if parts else ""
                if not tok:
                    continue
                if tok.isdigit():
                    try:
                        vid = int(tok)
                    except Exception:
                        vid = 0
                    if vid > 0:
                        mapped = str(hash_to_nick.get(vid, "") or numeric_id_map.get(vid, "") or "").strip()
                        if not mapped:
                            skipped_visit_unknown_numeric += 1
                        elif mapped.lower() not in known_nicks_generic:
                            bad_visit.add(tok)
                else:
                    nick = _token_to_known_nick(tok)
                    if nick and (not str(nick).isdigit()) and nick.lower() not in known_nicks_generic:
                        bad_visit.add(tok)
            elif k == "system":
                sys_nick = str(v or "").strip().upper()
                if sys_nick and sys_nick not in known_systems:
                    bad_systems.add(v.strip())
            elif k == "base":
                base_nick = str(v or "").strip().upper()
                if base_nick and base_nick not in known_bases:
                    bad_bases.add(v.strip())

        current_ship = _combo_item_nick(ship_archetype_cb)
        bad_ship_ui = bool(current_ship and current_ship.lower() not in known_ships)
        bad_equip_rows: list[int] = []
        for r in range(equip_tbl.rowCount()):
            item_cb = equip_tbl.cellWidget(r, 0)
            if not isinstance(item_cb, QComboBox):
                continue
            nick = _combo_item_nick(item_cb).strip()
            if nick and nick.lower() not in known_equip:
                bad_equip_rows.append(r)
        bad_cargo_rows: list[int] = []
        for r in range(cargo_tbl.rowCount()):
            item_cb = cargo_tbl.cellWidget(r, 0)
            if not isinstance(item_cb, QComboBox):
                continue
            nick = _combo_item_nick(item_cb).strip()
            if nick and nick.lower() not in known_equip:
                bad_cargo_rows.append(r)
        bad_rep_group_ui = False
        current_rep = _current_rep_group_nick()
        if current_rep and current_rep.lower() not in known_factions:
            bad_rep_group_ui = True
        bad_house_rows: list[int] = []
        for r in range(houses_tbl.rowCount()):
            it = houses_tbl.item(r, 0)
            fac = str(it.data(Qt.UserRole) if it else "").strip()
            if fac and fac.lower() not in known_factions:
                bad_house_rows.append(r)
        current_system_ui = _current_system_nick()
        bad_system_ui = bool(current_system_ui and current_system_ui.upper() not in known_systems)
        current_base_ui = _current_base_nick()
        bad_base_ui = bool(current_base_ui and current_base_ui.upper() not in known_bases)
        current_visit_ids = set(int(v) for v in set(state.get("visit_ids", set()) or set()) if int(v) > 0)
        bad_visit_ids_ui: set[int] = set()
        for vid in current_visit_ids:
            mapped = str(hash_to_nick.get(int(vid), "") or numeric_id_map.get(int(vid), "") or "").strip()
            if mapped and mapped.lower() not in known_nicks_generic:
                bad_visit_ids_ui.add(int(vid))

        if bad_ships:
            issues.append(tr("savegame_editor.validate.issue.ship").format(items=", ".join(sorted(bad_ships))))
        if bad_equip:
            issues.append(tr("savegame_editor.validate.issue.equip").format(items=", ".join(sorted(bad_equip)[:25])))
        if bad_cargo:
            issues.append(tr("savegame_editor.validate.issue.cargo").format(items=", ".join(sorted(bad_cargo)[:25])))
        if bad_factions:
            issues.append(tr("savegame_editor.validate.issue.factions").format(items=", ".join(sorted(bad_factions))))
        if bad_visit:
            issues.append(tr("savegame_editor.validate.issue.visited").format(items=", ".join(sorted(bad_visit)[:40])))
        if bad_systems:
            issues.append(tr("savegame_editor.validate.issue.systems").format(items=", ".join(sorted(bad_systems))))
        if bad_bases:
            issues.append(tr("savegame_editor.validate.issue.bases").format(items=", ".join(sorted(bad_bases))))

        if bad_ship_ui:
            suggestions.append(tr("savegame_editor.validate.suggest.ship"))
        if bad_equip_rows:
            suggestions.append(tr("savegame_editor.validate.suggest.equip").format(count=len(bad_equip_rows)))
        if bad_cargo_rows:
            suggestions.append(tr("savegame_editor.validate.suggest.cargo").format(count=len(bad_cargo_rows)))
        if bad_rep_group_ui:
            suggestions.append(tr("savegame_editor.validate.suggest.rep_group"))
        if bad_house_rows:
            suggestions.append(tr("savegame_editor.validate.suggest.houses").format(count=len(bad_house_rows)))
        if bad_system_ui:
            suggestions.append(tr("savegame_editor.validate.suggest.system"))
        if bad_base_ui:
            suggestions.append(tr("savegame_editor.validate.suggest.base"))
        if bad_visit_ids_ui:
            suggestions.append(tr("savegame_editor.validate.suggest.visited").format(count=len(bad_visit_ids_ui)))
        if skipped_visit_unknown_numeric > 0:
            suggestions.append(tr("savegame_editor.validate.suggest.visited_skip").format(count=skipped_visit_unknown_numeric))
        if fixed_hardpoints > 0:
            suggestions.append(tr("savegame_editor.validate.autofix_hardpoints_applied").format(count=fixed_hardpoints))

        if not issues:
            msg = tr("savegame_editor.validate.ok")
            if fixed_hardpoints > 0:
                msg += "\n\n" + tr("savegame_editor.validate.autofix_hardpoints_applied").format(count=fixed_hardpoints)
            QMessageBox.information(
                dlg,
                tr("savegame_editor.title"),
                msg,
            )
            return

        report = tr("savegame_editor.validate.issues_title") + "\n\n" + "\n".join(f"- {row}" for row in issues)
        if suggestions:
            report += "\n\n" + tr("savegame_editor.validate.suggest_title") + "\n" + "\n".join(f"- {row}" for row in suggestions)

        box = QMessageBox(dlg)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle(tr("savegame_editor.title"))
        box.setText(report)
        cleanup_btn = None
        if suggestions:
            cleanup_btn = box.addButton(tr("savegame_editor.validate.cleanup_apply"), QMessageBox.AcceptRole)
        box.addButton(tr("dlg.close"), QMessageBox.RejectRole)
        box.exec()
        if cleanup_btn is None or box.clickedButton() is not cleanup_btn:
            return

        if bad_ship_ui:
            ship_archetype_cb.setCurrentIndex(-1)
            ship_archetype_cb.setEditText("")
        for r in sorted(bad_equip_rows, reverse=True):
            equip_tbl.removeRow(r)
        for r in sorted(bad_cargo_rows, reverse=True):
            cargo_tbl.removeRow(r)
        if bad_rep_group_ui:
            rep_group_cb.setCurrentIndex(-1)
            rep_group_cb.setEditText("")
        for r in sorted(bad_house_rows, reverse=True):
            houses_tbl.removeRow(r)
        if bad_system_ui:
            system_cb.setCurrentIndex(-1)
            system_cb.setEditText("")
            _rebuild_base_combo("", "")
        if bad_base_ui:
            base_cb.setCurrentIndex(-1)
            base_cb.setEditText("")
        if bad_visit_ids_ui:
            cleaned_visits = set(int(v) for v in current_visit_ids if int(v) in known_visit_ids)
            _set_pending_visit_ids(cleaned_visits)
        _refresh_hardpoint_hint()
        self.statusBar().showMessage(tr("savegame_editor.pending_changes"))
        QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.validate.cleanup_done"))

    def _fmt_rep(v: float) -> str:
        return f"{float(v):.6f}".rstrip("0").rstrip(".")

    def _resolve_item_nick(raw_nick: str) -> str:
        raw = str(raw_nick or "").strip()
        if not raw:
            return ""
        if raw.isdigit():
            try:
                hid = int(raw)
            except Exception:
                hid = 0
            if hid > 0:
                mapped = str(hash_to_nick.get(hid, "") or "").strip()
                if mapped:
                    return mapped
        return raw

    def _item_ui_label(nick: str) -> str:
        raw = _resolve_item_nick(str(nick or "").strip())
        if not raw:
            return ""
        if raw.isdigit():
            try:
                mapped = str(numeric_id_map.get(int(raw), "") or "").strip()
            except Exception:
                mapped = ""
            if mapped:
                raw = mapped
        disp = str(item_name_map.get(raw.lower(), "") or "").strip()
        if not disp:
            fac_disp = str(nickname_labels.get(raw.lower(), "") or "").strip()
            if " - " in fac_disp:
                disp = fac_disp.split(" - ", 1)[1].strip()
        if disp and disp.lower() != raw.lower():
            return f"{raw} - {disp}"
        return raw

    def _item_from_ui(raw: str) -> str:
        txt = str(raw or "").strip()
        if not txt:
            return ""
        if " - " in txt:
            return txt.split(" - ", 1)[0].strip()
        return txt

    def _setup_item_combo(cb: QComboBox, nicks: list[str]) -> None:
        cb.setEditable(True)
        for nick in nicks:
            cb.addItem(_item_ui_label(nick), nick)

    def _set_item_combo_value(cb: QComboBox, nick: str) -> None:
        val = _resolve_item_nick(str(nick or "").strip())
        if not val:
            cb.setCurrentText("")
            return
        idx = cb.findData(val)
        if idx >= 0:
            cb.setCurrentIndex(idx)
            return
        cb.addItem(_item_ui_label(val), val)
        cb.setCurrentIndex(cb.count() - 1)

    def _combo_item_nick(cb: QComboBox) -> str:
        data = str(cb.currentData() or "").strip()
        if data:
            return _resolve_item_nick(data)
        return _resolve_item_nick(_item_from_ui(cb.currentText()))

    def _item_token_for_save(nick: str) -> str:
        raw = _resolve_item_nick(str(nick or "").strip())
        if not raw:
            return ""
        hid = int(self._fl_hash_nickname(raw))
        if hid > 0:
            return str(hid)
        return raw

    def _item_token_or_numeric_for_save(nick: str) -> str:
        raw = _resolve_item_nick(str(nick or "").strip())
        if not raw:
            return ""
        if raw.isdigit():
            return raw
        return _item_token_for_save(raw)

    def _current_ship_nick() -> str:
        return _combo_item_nick(ship_archetype_cb)

    def _ship_hardpoints(ship_nick: str) -> list[str]:
        return list(ship_hardpoints_by_nick.get(str(ship_nick or "").strip().lower(), []))

    def _equip_type(nick: str) -> str:
        return str(equip_type_by_nick.get(str(nick or "").strip().lower(), "") or "").strip().lower()

    def _equip_hp_types(nick: str) -> set[str]:
        vals = list(equip_hp_types_by_nick.get(str(nick or "").strip().lower(), []) or [])
        return {str(v).strip().lower() for v in vals if str(v).strip()}

    def _typed_filter_for_hardpoint(hardpoint: str, candidates: list[str]) -> list[str]:
        hp = str(hardpoint or "").strip().lower()
        if not hp:
            return list(candidates)
        out = list(candidates)
        if hp.startswith("hpshield"):
            out = [n for n in out if _equip_type(n) == "shieldgenerator"]
        elif hp.startswith("hpthruster"):
            out = [n for n in out if _equip_type(n) == "thruster"]
        elif hp.startswith("hpcountermeasure") or hp.startswith("hpcm"):
            out = [n for n in out if _equip_type(n) == "countermeasuredropper"]
        elif hp.startswith("hpmine"):
            out = [n for n in out if _equip_type(n) == "minedropper"]
        elif hp.startswith("hptorpedo"):
            out = [n for n in out if _equip_type(n) in {"gun", "cgun"}]
        return out

    def _ship_hp_types_for_hardpoint(ship_nick: str, hardpoint: str) -> set[str]:
        sn = str(ship_nick or "").strip().lower()
        hp = str(hardpoint or "").strip().lower()
        if not sn or not hp:
            return set()
        by_hp = dict(ship_hp_types_by_hardpoint_by_nick.get(sn, {}) or {})
        vals = list(by_hp.get(hp, []) or [])
        return {str(v).strip().lower() for v in vals if str(v).strip()}

    def _compatible_equip_nicks_for_hardpoint(hardpoint: str) -> list[str]:
        hp = str(hardpoint or "").strip().lower()
        if not hp:
            return list(equip_nicks)
        ship_types = _ship_hp_types_for_hardpoint(_current_ship_nick(), hp)
        if ship_types:
            by_type = []
            for n in equip_nicks:
                item_types = _equip_hp_types(n)
                if item_types and (item_types & ship_types):
                    by_type.append(n)
            by_type = _typed_filter_for_hardpoint(hp, by_type)
            if by_type:
                return by_type
        by_hpname = [n for n in equip_nicks if hp in _equip_hp_types(n)]
        by_hpname = _typed_filter_for_hardpoint(hp, by_hpname)
        if by_hpname:
            return by_hpname
        return _typed_filter_for_hardpoint(hp, list(equip_nicks))

    def _set_hardpoint_combo_value(cb: QComboBox, hardpoint: str) -> None:
        val = str(hardpoint or "").strip()
        if not val:
            idx_empty = cb.findData("")
            if idx_empty >= 0:
                cb.setCurrentIndex(idx_empty)
            else:
                cb.setCurrentIndex(-1)
                cb.setEditText("")
            return
        idx = cb.findData(val)
        if idx < 0:
            cb.addItem(val, val)
            idx = cb.count() - 1
        cb.setCurrentIndex(idx)

    def _hardpoint_from_widget(w: QWidget | None) -> str:
        if isinstance(w, QComboBox):
            return str(w.currentText() or "").strip()
        if isinstance(w, QLineEdit):
            return str(w.text() or "").strip()
        return ""

    def _table_row_for_widget(tbl: QTableWidget, w: QWidget | None, col: int) -> int:
        if w is None:
            return -1
        for r in range(tbl.rowCount()):
            if tbl.cellWidget(r, col) is w:
                return r
        return -1

    def _refresh_hardpoint_hint() -> None:
        ship_nick = _current_ship_nick()
        hp_all = _ship_hardpoints(ship_nick)
        if not hp_all:
            hardpoint_hint_lbl.setText(tr("savegame_editor.hardpoints_none"))
            return
        used: set[str] = set()
        for r in range(equip_tbl.rowCount()):
            hp = _hardpoint_from_widget(equip_tbl.cellWidget(r, 1))
            if hp:
                used.add(hp.lower())
        free = [hp for hp in hp_all if hp.lower() not in used]
        hardpoint_hint_lbl.setText(
            tr("savegame_editor.hardpoints_info").format(total=len(hp_all), used=len(used), free=max(0, len(free)))
            + " "
            + tr("savegame_editor.hardpoints_free_list").format(items=", ".join(free[:20]) if free else "-")
        )

    _setup_item_combo(ship_archetype_cb, ship_nicks)
    _setup_item_combo(com_body_cb, trent_body_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(body_cb, trent_body_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(com_head_cb, trent_head_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(head_cb, trent_head_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(com_lh_cb, trent_lh_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(lh_cb, trent_lh_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(com_rh_cb, trent_rh_nicks or trent_nicks or equip_nicks)
    _setup_item_combo(rh_cb, trent_rh_nicks or trent_nicks or equip_nicks)

    def _update_rep_color(spin: QDoubleSpinBox, value: float) -> None:
        if value < -0.61:
            spin.setStyleSheet("color: #d33f49; font-weight: 700;")
        elif value > 0.61:
            spin.setStyleSheet("color: #2f9e44; font-weight: 700;")
        else:
            spin.setStyleSheet("")

    def _insert_house_row(faction: str, rep: float) -> None:
        row = houses_tbl.rowCount()
        houses_tbl.insertRow(row)
        faction_nick = str(faction or "").strip()
        faction_label = faction_labels.get(faction_nick.lower(), self._faction_ui_label(faction_nick) or faction_nick)
        fac_item = QTableWidgetItem(faction_label)
        fac_item.setData(Qt.UserRole, faction_nick)
        fac_item.setFlags((fac_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled) & ~Qt.ItemIsEditable)
        houses_tbl.setItem(row, 0, fac_item)

        rep_spin = QDoubleSpinBox(dlg)
        rep_spin.setDecimals(3)
        rep_spin.setRange(-1.0, 1.0)
        rep_spin.setSingleStep(0.01)
        rep_spin.setValue(float(rep))
        _update_rep_color(rep_spin, float(rep))
        houses_tbl.setCellWidget(row, 1, rep_spin)

        rep_slider = QSlider(Qt.Horizontal, dlg)
        rep_slider.setRange(-100, 100)
        rep_slider.setSingleStep(1)
        rep_slider.setPageStep(5)
        rep_slider.setValue(int(round(float(rep) * 100.0)))
        houses_tbl.setCellWidget(row, 2, rep_slider)

        sync = {"busy": False}

        def _from_spin(v: float) -> None:
            if sync["busy"]:
                return
            sync["busy"] = True
            rep_slider.setValue(int(round(v * 100.0)))
            _update_rep_color(rep_spin, float(v))
            sync["busy"] = False

        def _from_slider(v: int) -> None:
            if sync["busy"]:
                return
            sync["busy"] = True
            rep_val = float(v) / 100.0
            rep_spin.setValue(rep_val)
            _update_rep_color(rep_spin, rep_val)
            sync["busy"] = False

        rep_spin.valueChanged.connect(_from_spin)
        rep_slider.valueChanged.connect(_from_slider)

    def _set_houses(rows: list[tuple[str, float]]) -> None:
        houses_tbl.setRowCount(0)
        for faction, rep in rows:
            _insert_house_row(faction, rep)

    def _locked_gate_ids_from_lines(lines: list[str]) -> set[int]:
        out: set[int] = set()
        for raw_line in lines:
            line = str(raw_line or "")
            core = line.split(";", 1)[0].strip()
            if not core or "=" not in core:
                continue
            key, value = core.split("=", 1)
            k = str(key or "").strip().lower()
            if k not in {"locked_gate", "npc_locked_gate"}:
                continue
            first = str(value or "").split(",", 1)[0].strip()
            try:
                hid = int(first)
            except Exception:
                continue
            if hid > 0:
                out.add(int(hid))
        return out

    def _visit_ids_from_lines(lines: list[str]) -> set[int]:
        out: set[int] = set()
        for raw_line in lines:
            line = str(raw_line or "")
            core = line.split(";", 1)[0].strip()
            if not core or "=" not in core:
                continue
            key, value = core.split("=", 1)
            if str(key or "").strip().lower() != "visit":
                continue
            first = str(value or "").split(",", 1)[0].strip()
            try:
                hid = int(first)
            except Exception:
                continue
            if hid > 0:
                out.add(int(hid))
        return out

    def _visit_line_map_from_lines(lines: list[str]) -> dict[int, str]:
        out: dict[int, str] = {}
        for raw_line in lines:
            line = str(raw_line or "")
            core = line.split(";", 1)[0].strip()
            if not core or "=" not in core:
                continue
            key, value = core.split("=", 1)
            if str(key or "").strip().lower() != "visit":
                continue
            raw_v = str(value or "").strip()
            first = raw_v.split(",", 1)[0].strip()
            try:
                hid = int(first)
            except Exception:
                continue
            if hid > 0 and hid not in out:
                out[int(hid)] = raw_v
        return out

    def _render_known_objects_map(locked_ids: set[int]) -> None:
        locked_scene.clear()
        systems_obj = dict(jump_data.get("systems", {}) or {})
        edges = list(jump_data.get("edges", []) or [])
        if not systems_obj or not edges:
            txt = locked_scene.addText(tr("savegame_editor.ids_none"))
            txt.setDefaultTextColor(map_colors["text_empty"])
            locked_view.set_base_rect(locked_scene.itemsBoundingRect().adjusted(-12, -12, 12, 12))
            return
        positions: dict[str, tuple[float, float]] = {}
        xs: list[float] = []
        ys: list[float] = []
        for key, row in systems_obj.items():
            x = float(row.get("x", 0.0) or 0.0)
            y = float(row.get("y", 0.0) or 0.0)
            positions[str(key).upper()] = (x, y)
            xs.append(x)
            ys.append(y)
        if not xs or not ys:
            txt = locked_scene.addText(tr("savegame_editor.ids_none"))
            txt.setDefaultTextColor(map_colors["text_empty"])
            return
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        w = max(1.0, max_x - min_x)
        h = max(1.0, max_y - min_y)
        scale = min(900.0 / w, 520.0 / h)
        node_pos: dict[str, QPointF] = {}
        for key, (x, y) in positions.items():
            sx = (x - min_x) * scale
            sy = (y - min_y) * scale
            node_pos[key] = QPointF(sx, sy)

        locked_systems: set[str] = set()
        for edge in edges:
            ids = [int(v) for v in list(edge.get("ids", []) or []) if int(v) > 0]
            if any(i in locked_ids for i in ids):
                locked_systems.add(str(edge.get("a", "")).upper())
                locked_systems.add(str(edge.get("b", "")).upper())

        for edge in edges:
            a = str(edge.get("a", "")).upper()
            b = str(edge.get("b", "")).upper()
            if a not in node_pos or b not in node_pos:
                continue
            ids = [int(v) for v in list(edge.get("ids", []) or []) if int(v) > 0]
            is_locked = any(i in locked_ids for i in ids)
            typ = str(edge.get("type", "hole") or "hole").lower()
            if is_locked:
                col = map_colors["line_locked"]
                width = 2.4
            else:
                col = map_colors["line_inactive"]
                width = 1.3
            pen = QPen(col, width)
            pen.setCosmetic(True)
            locked_scene.addLine(node_pos[a].x(), node_pos[a].y(), node_pos[b].x(), node_pos[b].y(), pen)

        for key, pt in node_pos.items():
            row = dict(systems_obj.get(key, {}) or {})
            nick = str(row.get("nickname", key) or key)
            disp = str(row.get("display", nick) or nick)
            r = 7.0 if key in locked_systems else 5.0
            fill = map_colors["node_locked"] if key in locked_systems else map_colors["node_inactive"]
            pen = QPen(map_colors["node_outline"], 1.0)
            pen.setCosmetic(True)
            node = locked_scene.addEllipse(pt.x() - r, pt.y() - r, r * 2.0, r * 2.0, pen, QBrush(fill))
            node.setData(0, key)
            label = locked_scene.addText(disp)
            label.setDefaultTextColor(map_colors["text_locked"] if key in locked_systems else map_colors["text_inactive"])
            label.setPos(pt.x() + 8.0, pt.y() - 10.0)
            label.setData(0, key)

        rect = locked_scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        locked_scene.setSceneRect(rect)
        locked_view.set_base_rect(rect)
        map_state["locked_ids"] = set(int(v) for v in locked_ids if int(v) > 0)

    def _render_visited_map(visit_ids: set[int]) -> None:
        visited_scene.clear()
        systems_obj = dict(jump_data.get("systems", {}) or {})
        edges = list(jump_data.get("edges", []) or [])
        if not systems_obj:
            txt = visited_scene.addText(tr("savegame_editor.ids_none"))
            txt.setDefaultTextColor(map_colors["text_empty"])
            visited_view.set_base_rect(visited_scene.itemsBoundingRect().adjusted(-12, -12, 12, 12))
            return
        positions: dict[str, tuple[float, float]] = {}
        hash_by_sys: dict[str, int] = {}
        xs: list[float] = []
        ys: list[float] = []
        for key, row in systems_obj.items():
            x = float(row.get("x", 0.0) or 0.0)
            y = float(row.get("y", 0.0) or 0.0)
            sk = str(key).upper()
            positions[sk] = (x, y)
            nick = str(row.get("nickname", sk) or sk)
            hash_by_sys[sk] = int(self._fl_hash_nickname(nick))
            xs.append(x)
            ys.append(y)
        if not xs or not ys:
            txt = visited_scene.addText(tr("savegame_editor.ids_none"))
            txt.setDefaultTextColor(map_colors["text_empty"])
            return
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)
        w = max(1.0, max_x - min_x)
        h = max(1.0, max_y - min_y)
        scale = min(900.0 / w, 520.0 / h)
        node_pos: dict[str, QPointF] = {}
        for key, (x, y) in positions.items():
            node_pos[key] = QPointF((x - min_x) * scale, (y - min_y) * scale)
        visited_systems: set[str] = {k for k, hv in hash_by_sys.items() if hv in visit_ids}
        for edge in edges:
            a = str(edge.get("a", "")).upper()
            b = str(edge.get("b", "")).upper()
            if a not in node_pos or b not in node_pos:
                continue
            edge_ids = [int(v) for v in list(edge.get("ids", []) or []) if int(v) > 0]
            edge_visited = any(v in visit_ids for v in edge_ids)
            if not edge_visited:
                edge_visited = (
                    hash_by_sys.get(a, 0) in visit_ids and hash_by_sys.get(b, 0) in visit_ids
                )
            if edge_visited:
                visited_systems.add(a)
                visited_systems.add(b)
            pen = QPen(map_colors["line_visited"] if edge_visited else map_colors["line_inactive"], 2.0 if edge_visited else 1.2)
            pen.setCosmetic(True)
            visited_scene.addLine(node_pos[a].x(), node_pos[a].y(), node_pos[b].x(), node_pos[b].y(), pen)
        for key, pt in node_pos.items():
            row = dict(systems_obj.get(key, {}) or {})
            disp = str(row.get("display", key) or key)
            is_visited = key in visited_systems
            r = 7.0 if is_visited else 5.0
            fill = map_colors["node_visited"] if is_visited else map_colors["node_inactive"]
            pen = QPen(map_colors["node_outline"], 1.0)
            pen.setCosmetic(True)
            node = visited_scene.addEllipse(pt.x() - r, pt.y() - r, r * 2.0, r * 2.0, pen, QBrush(fill))
            node.setData(0, key)
            label = visited_scene.addText(disp)
            label.setDefaultTextColor(map_colors["text_visited"] if is_visited else map_colors["text_inactive"])
            label.setPos(pt.x() + 8.0, pt.y() - 10.0)
            label.setData(0, key)
        rect = visited_scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        visited_scene.setSceneRect(rect)
        visited_view.set_base_rect(rect)
        map_state["visit_ids"] = set(int(v) for v in visit_ids if int(v) > 0)

    def _set_pending_locked_ids(locked_ids: set[int]) -> None:
        clean = set(int(v) for v in locked_ids if int(v) > 0)
        state["locked_ids"] = clean
        _render_known_objects_map(clean)

    def _set_pending_visit_ids(visit_ids: set[int]) -> None:
        clean = set(int(v) for v in visit_ids if int(v) > 0)
        state["visit_ids"] = clean
        _render_visited_map(clean)

    def _refresh_equip_row_filters(row: int) -> None:
        if row < 0 or row >= equip_tbl.rowCount():
            return
        item_cb = equip_tbl.cellWidget(row, 0)
        hp_cb = equip_tbl.cellWidget(row, 1)
        if not isinstance(item_cb, QComboBox) or not isinstance(hp_cb, QComboBox):
            return
        ship_hp_opts = _ship_hardpoints(_current_ship_nick())
        cur_item = _combo_item_nick(item_cb)
        cur_hp = _hardpoint_from_widget(hp_cb)
        hp_cb.blockSignals(True)
        hp_cb.clear()
        hp_cb.addItem("", "")
        for hp in ship_hp_opts:
            hp_cb.addItem(hp, hp)
        _set_hardpoint_combo_value(hp_cb, cur_hp)
        hp_cb.blockSignals(False)
        selected_hp = _hardpoint_from_widget(hp_cb)
        opts = _compatible_equip_nicks_for_hardpoint(selected_hp)
        item_cb.blockSignals(True)
        item_cb.clear()
        _setup_item_combo(item_cb, opts)
        if cur_item:
            _set_item_combo_value(item_cb, cur_item)
        else:
            item_cb.setCurrentIndex(-1)
            item_cb.setEditText("")
        item_cb.blockSignals(False)

    def _refresh_equip_row_filters_for_widget(w: QWidget | None) -> None:
        row = _table_row_for_widget(equip_tbl, w, 0)
        if row >= 0:
            _refresh_equip_row_filters(row)
            _refresh_hardpoint_hint()

    def _refresh_equip_row_filters_for_hp_widget(w: QWidget | None) -> None:
        row = _table_row_for_widget(equip_tbl, w, 1)
        if row >= 0:
            _refresh_equip_row_filters(row)
            _refresh_hardpoint_hint()

    def _add_equip_row(item_nick: str = "", hardpoint: str = "", extra: str = "") -> None:
        row = equip_tbl.rowCount()
        equip_tbl.insertRow(row)
        item_cb = QComboBox(dlg)
        _setup_item_combo(item_cb, equip_nicks)
        item_cb.setProperty("fl_extra", str(extra or "").strip())
        equip_tbl.setCellWidget(row, 0, item_cb)
        hp_cb = QComboBox(dlg)
        hp_cb.setEditable(False)
        hp_cb.addItem("", "")
        for hp in _ship_hardpoints(_current_ship_nick()):
            hp_cb.addItem(hp, hp)
        equip_tbl.setCellWidget(row, 1, hp_cb)
        if hardpoint:
            _set_hardpoint_combo_value(hp_cb, hardpoint)
        hp_cb.currentIndexChanged.connect(lambda _idx, w=hp_cb: _refresh_equip_row_filters_for_hp_widget(w))
        hp_cb.currentTextChanged.connect(lambda _txt, w=hp_cb: _refresh_equip_row_filters_for_hp_widget(w))
        _refresh_equip_row_filters(row)
        if item_nick:
            _set_item_combo_value(item_cb, item_nick)
            _refresh_equip_row_filters(row)
        _refresh_hardpoint_hint()

    def _add_cargo_row(item_nick: str = "", amount: int = 1, extra: str = ", , 0") -> None:
        row = cargo_tbl.rowCount()
        cargo_tbl.insertRow(row)
        item_cb = QComboBox(dlg)
        _setup_item_combo(item_cb, equip_nicks)
        _set_item_combo_value(item_cb, item_nick)
        item_cb.setProperty("fl_extra", str(extra or "").strip())
        cargo_tbl.setCellWidget(row, 0, item_cb)
        amt_spin = QSpinBox(dlg)
        amt_spin.setRange(0, 1_000_000)
        amt_spin.setValue(max(0, int(amount)))
        cargo_tbl.setCellWidget(row, 1, amt_spin)

    def _equip_rows() -> list[tuple[str, str, str]]:
        out: list[tuple[str, str, str]] = []
        for r in range(equip_tbl.rowCount()):
            item_cb = equip_tbl.cellWidget(r, 0)
            hp_w = equip_tbl.cellWidget(r, 1)
            if not isinstance(item_cb, QComboBox):
                continue
            nick = _combo_item_nick(item_cb)
            if not nick:
                continue
            hp = _hardpoint_from_widget(hp_w)
            extra = str(item_cb.property("fl_extra") or "").strip()
            out.append((nick, hp, extra))
        return out

    def _cargo_rows() -> list[tuple[str, int, str]]:
        out: list[tuple[str, int, str]] = []
        for r in range(cargo_tbl.rowCount()):
            item_cb = cargo_tbl.cellWidget(r, 0)
            amt_spin = cargo_tbl.cellWidget(r, 1)
            if not isinstance(item_cb, QComboBox):
                continue
            nick = _combo_item_nick(item_cb)
            if not nick:
                continue
            amount = int(amt_spin.value()) if isinstance(amt_spin, QSpinBox) else 0
            extra = str(item_cb.property("fl_extra") or "").strip()
            out.append((nick, amount, extra))
        return out

    def _refresh_equip_hardpoint_choices() -> None:
        for r in range(equip_tbl.rowCount()):
            _refresh_equip_row_filters(r)
        _refresh_hardpoint_hint()

    def _autofix_invalid_hardpoints(*, show_result: bool = True) -> int:
        ship_nick = _current_ship_nick()
        allowed = {str(hp or "").strip().lower() for hp in _ship_hardpoints(ship_nick) if str(hp or "").strip()}
        if not allowed:
            if show_result:
                QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.autofix.no_ship_hp"))
            return 0
        fixed_rows = 0
        fixed_hps: list[str] = []
        for r in range(equip_tbl.rowCount()):
            hp_cb = equip_tbl.cellWidget(r, 1)
            if not isinstance(hp_cb, QComboBox):
                continue
            hp = str(hp_cb.currentText() or "").strip()
            if not hp:
                continue
            if hp.lower() in allowed:
                continue
            _set_hardpoint_combo_value(hp_cb, "")
            fixed_rows += 1
            fixed_hps.append(hp)
        if fixed_rows <= 0:
            if show_result:
                QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.autofix.none_needed"))
            return 0
        _refresh_equip_hardpoint_choices()
        self.statusBar().showMessage(tr("savegame_editor.pending_changes"))
        if show_result:
            hp_list = ", ".join(sorted(set(fixed_hps), key=str.lower)[:20])
            QMessageBox.information(
                dlg,
                tr("savegame_editor.title"),
                tr("savegame_editor.autofix.done").format(
                    count=fixed_rows,
                    ship=_item_ui_label(ship_nick) or ship_nick or "?",
                    hps=hp_list or "-",
                ),
            )
        return fixed_rows

    def _current_system_nick() -> str:
        data = str(system_cb.currentData() or "").strip()
        if data:
            return data
        txt = str(system_cb.currentText() or "").strip()
        if " - " in txt:
            txt = txt.split(" - ", 1)[0].strip()
        return txt

    def _current_base_nick() -> str:
        data = str(base_cb.currentData() or "").strip()
        if data:
            return data
        txt = str(base_cb.currentText() or "").strip()
        m = re.match(r"^.*\(([^()]+)\)\s*$", txt)
        if m:
            inner = m.group(1).strip()
            if inner:
                return inner
        return txt

    def _set_story_lock_ui(active: bool, mission_num: int = 0) -> None:
        locked = bool(active)
        state["story_locked"] = locked
        system_cb.setEnabled(not locked)
        base_cb.setEnabled(not locked)
        if locked:
            story_lock_lbl.setText(tr("savegame_editor.story_lock").format(mn=int(mission_num)))
            story_lock_lbl.setVisible(True)
        else:
            story_lock_lbl.setText("")
            story_lock_lbl.setVisible(False)

    def _ensure_system_item(system_nick: str) -> None:
        sys_nick = str(system_nick or "").strip()
        if not sys_nick:
            return
        idx = system_cb.findData(sys_nick)
        if idx >= 0:
            system_cb.setCurrentIndex(idx)
            return
        sys_name = self._system_display_name(sys_nick, game_path).strip() or sys_nick
        sys_label = f"{sys_nick} - {sys_name}" if sys_name.lower() != sys_nick.lower() else sys_nick
        system_cb.addItem(sys_label, sys_nick)
        system_cb.setCurrentIndex(system_cb.count() - 1)

    def _rebuild_base_combo(system_nick: str, preferred_base: str = "") -> None:
        pref = str(preferred_base or "").strip()
        base_cb.blockSignals(True)
        base_cb.clear()
        for row in system_to_bases.get(str(system_nick or "").strip(), []):
            bnick = str(row.get("nickname", "")).strip()
            bdisp = str(row.get("display", "")).strip() or bnick
            if not bnick:
                continue
            label = f"{bdisp} ({bnick})" if bdisp.lower() != bnick.lower() else bnick
            base_cb.addItem(label, bnick)
        if pref:
            idx = base_cb.findData(pref)
            if idx >= 0:
                base_cb.setCurrentIndex(idx)
            else:
                base_cb.addItem(pref, pref)
                base_cb.setCurrentIndex(base_cb.count() - 1)
        elif base_cb.count() > 0:
            base_cb.setCurrentIndex(0)
        base_cb.blockSignals(False)

    def _set_rep_group_value(rep_group: str) -> None:
        rep = str(rep_group or "").strip()
        if not rep:
            rep_group_cb.setCurrentText("")
            return
        idx = rep_group_cb.findData(rep)
        if idx >= 0:
            rep_group_cb.setCurrentIndex(idx)
            return
        label = faction_labels.get(rep.lower(), self._faction_ui_label(rep) or rep)
        rep_group_cb.addItem(label, rep)
        rep_group_cb.setCurrentIndex(rep_group_cb.count() - 1)

    def _current_rep_group_nick() -> str:
        data = str(rep_group_cb.currentData() or "").strip()
        if data:
            return data
        raw = str(rep_group_cb.currentText() or "").strip()
        return self._faction_from_ui(raw) or raw

    def _current_houses() -> list[tuple[str, float]]:
        out: list[tuple[str, float]] = []
        for r in range(houses_tbl.rowCount()):
            item = houses_tbl.item(r, 0)
            if item is None:
                continue
            faction = str(item.data(Qt.UserRole) or "").strip()
            spin = houses_tbl.cellWidget(r, 1)
            if not faction or not isinstance(spin, QDoubleSpinBox):
                continue
            out.append((faction, float(spin.value())))
        return out

    def _parse_savegame(path: Path) -> tuple[bool, str]:
        try:
            raw = self._read_text_best_effort(path)
        except Exception as exc:
            return False, str(exc)
        lines = raw.splitlines()
        bounds = self._find_ini_section_bounds(lines, "Player", None)
        if bounds is None:
            return False, tr("savegame_editor.player_missing")
        s, e = bounds
        player_lines = lines[s:e]

        rank = 0
        money = 0
        description = ""
        rep_group = ""
        system = ""
        base = ""
        com_body = ""
        com_head = ""
        com_lefthand = ""
        com_righthand = ""
        body = ""
        head = ""
        lefthand = ""
        righthand = ""
        ship_archetype = ""
        equip_rows: list[tuple[str, str, str]] = []
        cargo_rows: list[tuple[str, int, str]] = []
        houses: list[tuple[str, float]] = []
        for raw_line in player_lines[1:]:
            line = str(raw_line).strip()
            if not line or line.startswith(";") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            k = key.strip().lower()
            v = val.strip()
            if k == "rank":
                try:
                    rank = int(float(v))
                except Exception:
                    rank = 0
            elif k == "money":
                try:
                    money = int(float(v))
                except Exception:
                    money = 0
            elif k == "rep_group":
                rep_group = v
            elif k == "description":
                description = v
            elif k == "system":
                system = v
            elif k == "base":
                base = v
            elif k == "com_body":
                com_body = v
            elif k == "com_head":
                com_head = v
            elif k == "com_lefthand":
                com_lefthand = v
            elif k == "com_righthand":
                com_righthand = v
            elif k == "body":
                body = v
            elif k == "head":
                head = v
            elif k == "lefthand":
                lefthand = v
            elif k == "righthand":
                righthand = v
            elif k == "ship_archetype":
                ship_archetype = v
            elif k == "equip":
                parts = [x.strip() for x in v.split(",")]
                if parts and parts[0]:
                    hardpoint = parts[1] if len(parts) > 1 else ""
                    if hardpoint and re.match(r"^[+-]?\d+(\.\d+)?$", hardpoint):
                        hardpoint = ""
                    extra = ", ".join(parts[2:]).strip() if len(parts) > 2 else "1"
                    equip_rows.append((parts[0], hardpoint, extra))
            elif k == "cargo":
                parts = [x.strip() for x in v.split(",")]
                if not parts or not parts[0]:
                    continue
                amount = 0
                for p in parts[1:]:
                    if not p:
                        continue
                    try:
                        amount = int(float(p))
                        break
                    except Exception:
                        continue
                extra = ", ".join(parts[2:]).strip() if len(parts) > 2 else ", , 0"
                cargo_rows.append((parts[0], amount, extra))
            elif k == "house":
                parts = [x.strip() for x in v.split(",", 1)]
                if len(parts) < 2:
                    continue
                try:
                    rep = float(parts[0])
                except Exception:
                    continue
                faction = parts[1]
                if faction:
                    houses.append((faction, rep))

        rank_spin.setValue(max(rank_spin.minimum(), min(rank_spin.maximum(), rank)))
        money_spin.setValue(max(money_spin.minimum(), min(money_spin.maximum(), money)))
        description_edit.setText(_decode_savegame_player_name(description))
        _set_rep_group_value(rep_group)
        _set_item_combo_value(com_body_cb, com_body)
        _set_item_combo_value(com_head_cb, com_head)
        _set_item_combo_value(com_lh_cb, com_lefthand)
        _set_item_combo_value(com_rh_cb, com_righthand)
        _set_item_combo_value(body_cb, body)
        _set_item_combo_value(head_cb, head)
        _set_item_combo_value(lh_cb, lefthand)
        _set_item_combo_value(rh_cb, righthand)
        _set_item_combo_value(ship_archetype_cb, ship_archetype)
        equip_tbl.setRowCount(0)
        for item_nick, hp, extra in equip_rows:
            _add_equip_row(item_nick, hp, extra)
        cargo_tbl.setRowCount(0)
        for item_nick, amount, extra in cargo_rows:
            _add_cargo_row(item_nick, amount, extra)
        _ensure_system_item(system)
        _rebuild_base_combo(system, preferred_base=base)
        houses.sort(key=lambda x: x[0].lower())
        _set_houses(houses)
        locked_ids = _locked_gate_ids_from_lines(player_lines)
        visit_ids = _visit_ids_from_lines(player_lines)
        state["locked_ids"] = set(locked_ids)
        state["visit_ids"] = set(visit_ids)
        state["visit_line_by_id"] = _visit_line_map_from_lines(player_lines)
        _set_pending_locked_ids(set(locked_ids))
        _set_pending_visit_ids(set(visit_ids))
        story_mission_num = 0
        story_bounds = self._find_ini_section_bounds(lines, "StoryInfo", None)
        if story_bounds is not None:
            ss, se = story_bounds
            for ln in lines[ss + 1:se]:
                core = str(ln or "").split(";", 1)[0].strip()
                if not core or "=" not in core:
                    continue
                k, v = core.split("=", 1)
                if str(k or "").strip().lower() != "missionnum":
                    continue
                try:
                    story_mission_num = int(float(str(v or "").strip()))
                except Exception:
                    story_mission_num = 0
                break
        _set_savegame_loaded_state()
        _set_story_lock_ui(1 <= int(story_mission_num) <= 12, story_mission_num)
        _set_editor_title(path)
        info_lbl.setText("")
        state["path"] = path
        return True, ""

    def _parse_with_loading(path: Path) -> tuple[bool, str]:
        _set_loading(True)
        try:
            return _parse_savegame(path)
        finally:
            _set_loading(False)

    def _decode_savegame_player_name(raw_name: str) -> str:
        txt = str(raw_name or "").strip()
        if not txt:
            return ""
        if re.fullmatch(r"[0-9A-Fa-f]+", txt) and len(txt) % 2 == 0:
            try:
                blob = bytes.fromhex(txt)
            except Exception:
                blob = b""
            if blob:
                for enc in ("utf-16-be", "utf-16-le", "utf-8", "cp1252", "latin1"):
                    try:
                        val = blob.decode(enc, errors="ignore").replace("\x00", "").strip()
                    except Exception:
                        val = ""
                    if val:
                        return val
        return txt

    def _encode_savegame_player_name(raw_name: str) -> str:
        txt = str(raw_name or "").strip()
        if not txt:
            return ""
        if re.fullmatch(r"[0-9A-Fa-f]+", txt) and len(txt) % 2 == 0:
            return txt
        try:
            return txt.encode("utf-16-be").hex().upper()
        except Exception:
            return txt

    def _read_savegame_player_name(path: Path) -> str:
        try:
            raw = self._read_text_best_effort(path)
        except Exception:
            return ""
        lines = raw.splitlines()
        bounds = self._find_ini_section_bounds(lines, "Player", None)
        if bounds is None:
            return ""
        s, e = bounds
        player_values: dict[str, str] = {}
        for raw_line in lines[s + 1:e]:
            line = str(raw_line or "").strip()
            if not line or line.startswith(";") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            k = str(key or "").strip().lower()
            if not k:
                continue
            if k not in player_values:
                player_values[k] = str(val or "").strip()
        if str(player_values.get("description", "")).strip():
            return _decode_savegame_player_name(str(player_values.get("description", "")))
        if str(player_values.get("name", "")).strip():
            return _decode_savegame_player_name(str(player_values.get("name", "")))
        return ""

    def _refresh_savegame_list(*, select_path: Path | None = None, auto_load: bool = False) -> None:
        save_dir = _save_dir()
        files: list[Path] = []
        if save_dir.exists() and save_dir.is_dir():
            try:
                files = sorted(
                    [p for p in save_dir.iterdir() if p.is_file() and p.suffix.lower() == ".fl"],
                    key=lambda p: p.name.lower(),
                )
            except Exception:
                files = []
        state["updating_savegame_cb"] = True
        savegame_cb.clear()
        for fp in files:
            ingame_name = _read_savegame_player_name(fp)
            label = f"{fp.name} - {ingame_name}" if ingame_name else fp.name
            savegame_cb.addItem(label, str(fp))
        state["updating_savegame_cb"] = False
        if not files:
            savegame_cb.setCurrentIndex(-1)
            _set_story_lock_ui(False, 0)
            _set_no_savegame_state()
            return
        target = None
        if select_path is not None:
            target = str(select_path)
        elif isinstance(state.get("path"), Path):
            target = str(state.get("path"))
        selected = False
        if target:
            idx = savegame_cb.findData(target)
            if idx >= 0:
                savegame_cb.setCurrentIndex(idx)
                selected = True
        if not selected:
            savegame_cb.setCurrentIndex(-1)
            _set_no_savegame_state()
        if auto_load and savegame_cb.currentIndex() >= 0:
            _load_selected()

    def _load_selected() -> None:
        chosen = str(savegame_cb.currentData() or "").strip()
        if not chosen:
            _set_no_savegame_state()
            return
        ok, msg = _parse_with_loading(Path(chosen))
        if not ok:
            _set_no_savegame_state()
            QMessageBox.warning(dlg, tr("savegame_editor.title"), msg)

    def _apply_save_dir() -> bool:
        raw = save_dir_edit.text().strip()
        path = self._canonical_savegame_dir_from_input(raw)
        save_dir_edit.setText(str(path))
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(
                dlg,
                tr("savegame_editor.title"),
                tr("savegame_editor.path_dir_invalid").format(path=str(path)),
            )
            return False
        self._cfg.set("settings.savegame_path", str(path))
        self.statusBar().showMessage(tr("savegame_editor.path_saved").format(path=str(path)))
        _refresh_savegame_list(auto_load=False)
        return True

    def _apply_game_path() -> bool:
        nonlocal game_path, faction_labels, templates, nickname_labels, numeric_id_map
        nonlocal item_name_map, ship_nicks, equip_nicks, trent_nicks, trent_body_nicks
        nonlocal trent_head_nicks, trent_lh_nicks, trent_rh_nicks, ship_hardpoints_by_nick
        nonlocal ship_hp_types_by_hardpoint_by_nick
        nonlocal equip_type_by_nick, equip_hp_types_by_nick, hash_to_nick
        nonlocal jump_data, system_label_by_nick, system_to_bases
        raw_gp = str(game_path_edit.text() or "").strip()
        gp_path = self._canonical_game_dir_from_input(raw_gp)
        game_path = str(gp_path).strip()
        game_path_edit.setText(game_path)
        if not game_path or self._find_freelancer_exe(gp_path) is None:
            QMessageBox.warning(
                dlg,
                tr("savegame_editor.title"),
                tr("mod_manager.launch.no_exe").format(path=game_path or raw_gp),
            )
            return False
        self._cfg.set("settings.savegame_game_path", game_path)
        faction_labels = self._savegame_editor_load_faction_labels(game_path)
        templates = self._savegame_editor_collect_rep_templates(game_path)
        nickname_labels = self._savegame_editor_collect_nickname_labels(game_path)
        numeric_id_map = self._savegame_editor_collect_numeric_id_map(game_path)
        system_label_by_nick = {}
        system_to_bases = {}
        if game_path:
            try:
                for row in self._npc_collect_bases(game_path):
                    base_nick = str(row.get("nickname", "")).strip()
                    base_disp = str(row.get("display", "")).strip() or base_nick
                    sys_nick = str(row.get("system", "")).strip()
                    if not base_nick or not sys_nick:
                        continue
                    sys_name = self._system_display_name(sys_nick, game_path).strip() or sys_nick
                    sys_label = f"{sys_nick} - {sys_name}" if sys_name.lower() != sys_nick.lower() else sys_nick
                    system_label_by_nick[sys_nick] = sys_label
                    system_to_bases.setdefault(sys_nick, []).append({"nickname": base_nick, "display": base_disp})
            except Exception:
                system_label_by_nick = {}
                system_to_bases = {}
        for sys_nick, rows in system_to_bases.items():
            rows.sort(key=lambda r: str(r.get("display", "")).lower())
        item_data_new = self._savegame_editor_collect_item_data(game_path)
        item_name_map = dict(item_data_new.get("item_name_map", {}) or {})
        ship_nicks = list(item_data_new.get("ship_nicks", []) or [])
        equip_nicks = list(item_data_new.get("equip_nicks", []) or [])
        trent_nicks = list(item_data_new.get("trent_nicks", []) or [])
        trent_body_nicks = list(item_data_new.get("trent_body_nicks", []) or [])
        trent_head_nicks = list(item_data_new.get("trent_head_nicks", []) or [])
        trent_lh_nicks = list(item_data_new.get("trent_lh_nicks", []) or [])
        trent_rh_nicks = list(item_data_new.get("trent_rh_nicks", []) or [])
        ship_hardpoints_by_nick = {
            str(k): list(v) for k, v in dict(item_data_new.get("ship_hardpoints_by_nick", {}) or {}).items()
        }
        ship_hp_types_by_hardpoint_by_nick = {
            str(k): {str(hk): list(hv) for hk, hv in dict(hmap).items()}
            for k, hmap in dict(item_data_new.get("ship_hp_types_by_hardpoint_by_nick", {}) or {}).items()
        }
        equip_type_by_nick = {
            str(k): str(v) for k, v in dict(item_data_new.get("equip_type_by_nick", {}) or {}).items()
        }
        equip_hp_types_by_nick = {
            str(k): list(v) for k, v in dict(item_data_new.get("equip_hp_types_by_nick", {}) or {}).items()
        }
        hash_to_nick = {int(k): str(v) for k, v in dict(item_data_new.get("hash_to_nick", {}) or {}).items()}
        jump_data = self._savegame_editor_collect_jump_connections(game_path)
        rep_group_cb.blockSignals(True)
        rep_group_cb.clear()
        for nick in sorted(self._cached_factions, key=str.lower):
            label = faction_labels.get(str(nick).strip().lower(), self._faction_ui_label(nick) or str(nick))
            rep_group_cb.addItem(label, str(nick))
        rep_group_cb.blockSignals(False)
        template_cb.blockSignals(True)
        template_cb.clear()
        for tpl in templates:
            template_cb.addItem(str(tpl.get("name") or ""), tpl)
        template_cb.setEnabled(bool(templates))
        apply_template_btn.setEnabled(bool(templates))
        template_cb.setCurrentIndex(-1)
        template_cb.blockSignals(False)
        cur_sys = _current_system_nick()
        system_cb.blockSignals(True)
        system_cb.clear()
        for sys_nick in sorted(system_to_bases.keys(), key=lambda s: str(system_label_by_nick.get(s, s)).lower()):
            system_cb.addItem(system_label_by_nick.get(sys_nick, sys_nick), sys_nick)
        if cur_sys:
            idx = system_cb.findData(cur_sys)
            if idx >= 0:
                system_cb.setCurrentIndex(idx)
            elif system_cb.count() > 0:
                system_cb.setCurrentIndex(0)
        system_cb.blockSignals(False)
        _rebuild_base_combo(_current_system_nick(), _current_base_nick())
        ship_archetype_cb.blockSignals(True)
        ship_archetype_cb.clear()
        _setup_item_combo(ship_archetype_cb, ship_nicks)
        ship_archetype_cb.blockSignals(False)
        trent_current = [_combo_item_nick(cb) for cb in trent_item_cbs]
        trent_sources: list[tuple[QComboBox, list[str]]] = [
            (com_body_cb, trent_body_nicks or trent_nicks or equip_nicks),
            (com_head_cb, trent_head_nicks or trent_nicks or equip_nicks),
            (com_lh_cb, trent_lh_nicks or trent_nicks or equip_nicks),
            (com_rh_cb, trent_rh_nicks or trent_nicks or equip_nicks),
            (body_cb, trent_body_nicks or trent_nicks or equip_nicks),
            (head_cb, trent_head_nicks or trent_nicks or equip_nicks),
            (lh_cb, trent_lh_nicks or trent_nicks or equip_nicks),
            (rh_cb, trent_rh_nicks or trent_nicks or equip_nicks),
        ]
        for idx, (cb, source) in enumerate(trent_sources):
            cb.blockSignals(True)
            cb.clear()
            _setup_item_combo(cb, source)
            _set_item_combo_value(cb, trent_current[idx] if idx < len(trent_current) else "")
            cb.blockSignals(False)
        _refresh_equip_hardpoint_choices()
        cur_path = state.get("path")
        if isinstance(cur_path, Path):
            ok, msg = _parse_with_loading(cur_path)
            if not ok:
                QMessageBox.warning(dlg, tr("savegame_editor.title"), msg)
        self.statusBar().showMessage(tr("savegame_editor.game_path_saved").format(path=game_path))
        return True

    def _open_path_settings() -> None:
        pd = QDialog(dlg)
        pd.setWindowTitle(tr("savegame_editor.path_settings"))
        pd.resize(760, 180)
        pl = QVBoxLayout(pd)
        form = QFormLayout()
        sg_row = QWidget(pd)
        sg_l = QHBoxLayout(sg_row)
        sg_l.setContentsMargins(0, 0, 0, 0)
        sg_l.setSpacing(6)
        sg_edit = QLineEdit(save_dir_edit.text().strip(), pd)
        sg_l.addWidget(sg_edit, 1)
        sg_browse = QPushButton(tr("welcome.browse"), pd)
        sg_l.addWidget(sg_browse)
        form.addRow(tr("savegame_editor.path_dir"), sg_row)
        gm_row = QWidget(pd)
        gm_l = QHBoxLayout(gm_row)
        gm_l.setContentsMargins(0, 0, 0, 0)
        gm_l.setSpacing(6)
        gm_edit = QLineEdit(game_path_edit.text().strip(), pd)
        gm_l.addWidget(gm_edit, 1)
        gm_browse = QPushButton(tr("welcome.browse"), pd)
        gm_l.addWidget(gm_browse)
        form.addRow(tr("savegame_editor.game_path"), gm_row)
        pl.addLayout(form)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        ok_btn = QPushButton(tr("savegame_editor.path_apply"), pd)
        cancel_btn = QPushButton(_tr_or("dlg.cancel", "Cancel"), pd)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        pl.addLayout(btn_row)

        def _browse_save_path() -> None:
            start = sg_edit.text().strip() or str(Path.home())
            chosen = QFileDialog.getExistingDirectory(pd, tr("welcome.browse_title"), start)
            if chosen:
                sg_edit.setText(chosen)

        def _browse_game_path() -> None:
            start = gm_edit.text().strip() or str(Path.home())
            chosen = QFileDialog.getExistingDirectory(pd, tr("welcome.browse_title"), start)
            if chosen:
                gm_edit.setText(chosen)

        def _accept() -> None:
            save_dir_edit.setText(sg_edit.text().strip())
            game_path_edit.setText(gm_edit.text().strip())
            if not _apply_save_dir():
                return
            if not _apply_game_path():
                return
            pd.accept()

        sg_browse.clicked.connect(_browse_save_path)
        gm_browse.clicked.connect(_browse_game_path)
        ok_btn.clicked.connect(_accept)
        cancel_btn.clicked.connect(pd.reject)
        pd.exec()

    def _unlock_all_connections() -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.no_file"))
            return
        _set_pending_locked_ids(set())
        info_lbl.setText(tr("savegame_editor.unlocked_all").format(count=0))
        self.statusBar().showMessage(tr("savegame_editor.pending_changes"))

    def _unlock_system_connections(system_key: str) -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            return
        skey = str(system_key or "").strip().upper()
        if not skey:
            return
        ids: set[int] = set()
        for edge in list(jump_data.get("edges", []) or []):
            a = str(edge.get("a", "")).upper()
            b = str(edge.get("b", "")).upper()
            if skey not in {a, b}:
                continue
            for v in list(edge.get("ids", []) or []):
                try:
                    hid = int(v)
                except Exception:
                    hid = 0
                if hid > 0:
                    ids.add(hid)
        current_locked = set(int(v) for v in set(state.get("locked_ids", set()) or set()) if int(v) > 0)
        if not ids or not current_locked:
            return
        new_locked = set(current_locked)
        new_locked.difference_update(ids)
        removed = max(0, len(current_locked) - len(new_locked))
        if removed <= 0:
            return
        _set_pending_locked_ids(new_locked)
        sys_row = dict(dict(jump_data.get("systems", {}) or {}).get(skey, {}) or {})
        disp = str(sys_row.get("display", skey) or skey)
        info_lbl.setText(tr("savegame_editor.unlocked_system").format(system=disp, count=removed))
        self.statusBar().showMessage(tr("savegame_editor.pending_changes"))

    def _visit_unlock_all_connections() -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.no_file"))
            return
        gate_ids = sorted(int(v) for v in set(jump_data.get("all_gate_ids", set()) or set()) if int(v) > 0)
        if not gate_ids:
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.ids_none"))
            return
        system_ids: set[int] = set()
        for row in dict(jump_data.get("systems", {}) or {}).values():
            sys_nick = str(dict(row or {}).get("nickname", "") or "").strip()
            if not sys_nick:
                continue
            hid = int(self._fl_hash_nickname(sys_nick))
            if hid > 0:
                system_ids.add(hid)
        all_ids = sorted(set(gate_ids) | system_ids)
        current_visit = set(int(v) for v in set(state.get("visit_ids", set()) or set()) if int(v) > 0)
        merged = set(current_visit)
        merged.update(int(v) for v in all_ids)
        _set_pending_visit_ids(merged)
        info_lbl.setText(
            tr("savegame_editor.visited_all").format(count=len(all_ids))
            + f" (JH/JG: {len(gate_ids)}, Systems: {len(system_ids)})"
        )
        self.statusBar().showMessage(tr("savegame_editor.pending_changes"))

    def _pick_file() -> None:
        cur = state.get("path")
        if isinstance(cur, Path):
            start_dir = str(cur.parent)
        else:
            start_dir = str(_save_dir())
        chosen, _flt = QFileDialog.getOpenFileName(
            dlg,
            tr("savegame_editor.open"),
            start_dir,
            tr("savegame_editor.file_filter"),
        )
        if not chosen:
            return
        chosen_path = Path(chosen)
        save_dir_edit.setText(str(chosen_path.parent))
        _apply_save_dir()
        ok, msg = _parse_with_loading(chosen_path)
        if not ok:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), msg)
            return
        _refresh_savegame_list(select_path=chosen_path, auto_load=False)

    def _reload() -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.no_file"))
            return
        ok, msg = _parse_with_loading(cur)
        if not ok:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), msg)

    def _apply_template() -> None:
        tpl = template_cb.currentData()
        if not isinstance(tpl, dict):
            return
        houses_obj = tpl.get("houses")
        if not isinstance(houses_obj, dict) or not houses_obj:
            return
        try:
            houses_in = {str(k).strip(): float(v) for k, v in houses_obj.items() if str(k).strip()}
        except Exception:
            return
        template_faction = str(tpl.get("faction") or "").strip()
        rows: list[tuple[str, float]] = []
        for fac, val in houses_in.items():
            rep = float(val)
            rep = max(-0.91, min(0.91, rep))
            rows.append((fac, rep))
        rows.sort(key=lambda x: x[0].lower())
        _set_houses(rows)
        if template_faction:
            _set_rep_group_value(template_faction)
        info_lbl.setText(
            tr("savegame_editor.template_applied").format(
                template=str(tpl.get("name") or ""),
                faction=self._faction_ui_label(template_faction) or template_faction or tr("savegame_editor.template_none"),
            )
        )

    def _save() -> None:
        cur = state.get("path")
        if not isinstance(cur, Path):
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.no_file"))
            return
        try:
            raw = self._read_text_best_effort(cur)
        except Exception as exc:
            QMessageBox.critical(dlg, tr("msg.save_error"), tr("savegame_editor.save_failed").format(error=exc))
            return
        newline = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.splitlines()
        bounds = self._find_ini_section_bounds(lines, "Player", None)
        if bounds is None:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), tr("savegame_editor.player_missing"))
            return
        s, e = bounds
        player = list(lines[s:e])
        orig_system = ""
        orig_base = ""
        for ln in player[1:]:
            core = str(ln or "").split(";", 1)[0].strip()
            if not core or "=" not in core:
                continue
            k, v = core.split("=", 1)
            kl = str(k or "").strip().lower()
            vv = str(v or "").strip()
            if kl == "system" and not orig_system:
                orig_system = vv
            elif kl == "base" and not orig_base:
                orig_base = vv

        new_system = _current_system_nick()
        new_base = _current_base_nick()

        # Freelancer can crash when moving system/base in an active story mission save.
        story_mission_num = 0
        story_bounds = self._find_ini_section_bounds(lines, "StoryInfo", None)
        if story_bounds is not None:
            ss, se = story_bounds
            for ln in lines[ss + 1:se]:
                core = str(ln or "").split(";", 1)[0].strip()
                if not core or "=" not in core:
                    continue
                k, v = core.split("=", 1)
                if str(k or "").strip().lower() != "missionnum":
                    continue
                try:
                    story_mission_num = int(float(str(v or "").strip()))
                except Exception:
                    story_mission_num = 0
                break
        story_active = 1 <= int(story_mission_num) <= 12
        if story_active:
            changed_system = bool(orig_system and new_system) and (orig_system.strip().lower() != new_system.strip().lower())
            changed_base = bool(orig_base and new_base) and (orig_base.strip().lower() != new_base.strip().lower())
            if changed_system or changed_base:
                QMessageBox.warning(
                    dlg,
                    tr("savegame_editor.title"),
                    tr("savegame_editor.story_save_blocked").format(mn=story_mission_num),
                )
                return

        player, _ = self._set_single_key_line_in_section(player, "rank", f"rank = {int(rank_spin.value())}")
        player, _ = self._set_single_key_line_in_section(player, "money", f"money = {int(money_spin.value())}")
        enc_description = _encode_savegame_player_name(description_edit.text())
        if enc_description:
            player, _ = self._set_single_key_line_in_section(player, "description", f"description = {enc_description}")
        player, _ = self._set_single_key_line_in_section(player, "rep_group", f"rep_group = {_current_rep_group_nick()}")
        player, _ = self._set_single_key_line_in_section(player, "system", f"system = {new_system}")
        player, _ = self._set_single_key_line_in_section(player, "base", f"base = {new_base}")
        player, _ = self._set_single_key_line_in_section(
            player, "com_body", f"com_body = {_item_token_or_numeric_for_save(_combo_item_nick(com_body_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "com_head", f"com_head = {_item_token_or_numeric_for_save(_combo_item_nick(com_head_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "com_lefthand", f"com_lefthand = {_item_token_or_numeric_for_save(_combo_item_nick(com_lh_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "com_righthand", f"com_righthand = {_item_token_or_numeric_for_save(_combo_item_nick(com_rh_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "body", f"body = {_item_token_or_numeric_for_save(_combo_item_nick(body_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "head", f"head = {_item_token_or_numeric_for_save(_combo_item_nick(head_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "lefthand", f"lefthand = {_item_token_or_numeric_for_save(_combo_item_nick(lh_cb))}"
        )
        player, _ = self._set_single_key_line_in_section(
            player, "righthand", f"righthand = {_item_token_or_numeric_for_save(_combo_item_nick(rh_cb))}"
        )
        current_ship_nick = _combo_item_nick(ship_archetype_cb)
        ship_token = _item_token_for_save(current_ship_nick)
        player, _ = self._set_single_key_line_in_section(player, "ship_archetype", f"ship_archetype = {ship_token}")

        allowed_hps = {str(hp or "").strip().lower() for hp in _ship_hardpoints(current_ship_nick) if str(hp or "").strip()}
        invalid_hp_rows: list[tuple[str, str]] = []
        for item_nick, hardpoint, _extra in _equip_rows():
            hp = str(hardpoint or "").strip()
            if not hp:
                continue
            if allowed_hps and hp.lower() not in allowed_hps:
                invalid_hp_rows.append((item_nick, hp))
        if invalid_hp_rows:
            hp_list = sorted({hp for _item, hp in invalid_hp_rows}, key=str.lower)
            QMessageBox.warning(
                dlg,
                tr("savegame_editor.title"),
                tr("savegame_editor.invalid_hardpoints").format(
                    count=len(invalid_hp_rows),
                    ship=_item_ui_label(current_ship_nick) or current_ship_nick or "?",
                    hps=", ".join(hp_list[:20]),
                ),
            )
            return

        house_lines: list[str] = []
        for faction, rep in _current_houses():
            house_lines.append(f"house = {_fmt_rep(rep)}, {faction}")

        equip_lines: list[str] = []
        for item_nick, hardpoint, extra in _equip_rows():
            item_token = _item_token_for_save(item_nick)
            if not item_token:
                continue
            tail = str(extra or "").strip()
            if not tail:
                tail = "1"
            if hardpoint:
                equip_lines.append(f"equip = {item_token}, {hardpoint}, {tail}")
            else:
                equip_lines.append(f"equip = {item_token}, , {tail}")

        cargo_lines: list[str] = []
        for item_nick, amount, extra in _cargo_rows():
            item_token = _item_token_for_save(item_nick)
            if not item_token:
                continue
            tail = str(extra or "").strip()
            if not tail:
                tail = ", , 0"
            cargo_lines.append(f"cargo = {item_token}, {int(amount)}, {tail}")

        def _line_key(raw_line: str) -> str:
            core = str(raw_line or "").split(";", 1)[0].strip()
            if not core or "=" not in core:
                return ""
            return str(core.split("=", 1)[0] or "").strip().lower()

        def _replace_key_block(
            section_lines: list[str], keys: set[str], replacement_lines: list[str]
        ) -> list[str]:
            if not section_lines:
                return []
            header = section_lines[0]
            body = list(section_lines[1:])
            first_idx: int | None = None
            kept: list[str] = []
            for ln in body:
                if _line_key(ln) in keys:
                    if first_idx is None:
                        first_idx = len(kept)
                    continue
                kept.append(ln)
            if replacement_lines:
                ins = first_idx if first_idx is not None else len(kept)
                kept = kept[:ins] + list(replacement_lines) + kept[ins:]
            return [header] + kept

        pending_locked = sorted(int(v) for v in set(state.get("locked_ids", set()) or set()) if int(v) > 0)
        pending_visit = sorted(int(v) for v in set(state.get("visit_ids", set()) or set()) if int(v) > 0)
        visit_line_by_id = dict(state.get("visit_line_by_id", {}) or {})
        lock_lines = [f"locked_gate = {hid}" for hid in pending_locked]
        visit_lines: list[str] = []
        for hid in pending_visit:
            raw_v = str(visit_line_by_id.get(int(hid), "") or "").strip()
            if not raw_v:
                raw_v = f"{int(hid)}, 1"
            visit_lines.append(f"visit = {raw_v}")
        player = _replace_key_block(player, {"locked_gate", "npc_locked_gate"}, lock_lines)
        player = _replace_key_block(player, {"visit"}, visit_lines)
        player = _replace_key_block(player, {"equip"}, equip_lines)
        player = _replace_key_block(player, {"cargo"}, cargo_lines)
        player = _replace_key_block(player, {"house"}, house_lines)
        out_lines = lines[:s] + player + lines[e:]

        backup = cur.with_name(f"{cur.name}.FLAtlasBAK")
        try:
            shutil.copy2(str(cur), str(backup))
            text = newline.join(out_lines)
            if not text.endswith(newline):
                text += newline
            self._write_text_preserve_format(cur, text)
        except Exception as exc:
            QMessageBox.critical(dlg, tr("msg.save_error"), tr("savegame_editor.save_failed").format(error=exc))
            return
        self.statusBar().showMessage(tr("savegame_editor.saved").format(path=str(cur), backup=str(backup)))
        info_lbl.setText(tr("savegame_editor.saved").format(path=str(cur), backup=str(backup)))

    act_file_refresh = file_menu.addAction(tr("savegame_editor.refresh_list"))
    act_file_load_selected = file_menu.addAction(tr("savegame_editor.load_selected"))
    file_menu.addSeparator()
    act_file_open = file_menu.addAction(tr("savegame_editor.open"))
    act_file_reload = file_menu.addAction(tr("savegame_editor.reload"))
    act_file_save = file_menu.addAction(tr("savegame_editor.save"))
    file_menu.addSeparator()
    act_file_close = file_menu.addAction(tr("dlg.close"))
    act_settings_paths = settings_menu.addAction(tr("savegame_editor.path_settings"))
    act_help_quick = help_menu.addAction(tr("savegame_editor.help.quick"))
    act_help_updates = help_menu.addAction(tr("savegame_editor.help.updates"))
    help_menu.addSeparator()
    act_help_reset_config = help_menu.addAction(tr("savegame_editor.help.reset_config"))
    settings_menu.addSeparator()
    theme_group = QActionGroup(dlg)
    theme_group.setExclusive(True)
    theme_actions: dict[str, object] = {}
    for t in THEME_ORDER:
        a = theme_menu.addAction(t)
        a.setCheckable(True)
        theme_group.addAction(a)
        theme_actions[t] = a
    lang_actions: dict[str, object] = {}
    for code in available_languages():
        c = str(code or "").strip()
        if not c:
            continue
        label = {"de": "Deutsch", "en": "English"}.get(c.lower(), c.upper())
        act = language_menu.addAction(label)
        act.setCheckable(True)
        act.setChecked(c.lower() == str(get_language() or "").lower())
        lang_actions[c] = act

    ship_archetype_cb.currentIndexChanged.connect(lambda _idx: _refresh_equip_hardpoint_choices())
    ship_archetype_cb.currentTextChanged.connect(lambda _txt: _refresh_equip_hardpoint_choices())
    system_cb.currentIndexChanged.connect(lambda _idx: _rebuild_base_combo(_current_system_nick(), _current_base_nick()))
    system_cb.currentTextChanged.connect(lambda _txt: _rebuild_base_combo(_current_system_nick(), _current_base_nick()))
    equip_add_btn.clicked.connect(lambda: _add_equip_row("", ""))
    equip_del_btn.clicked.connect(
        lambda: (equip_tbl.removeRow(equip_tbl.currentRow()), _refresh_hardpoint_hint()) if equip_tbl.currentRow() >= 0 else None
    )
    equip_autofix_btn.clicked.connect(_autofix_invalid_hardpoints)
    cargo_add_btn.clicked.connect(lambda: _add_cargo_row("", 1))
    cargo_del_btn.clicked.connect(lambda: cargo_tbl.removeRow(cargo_tbl.currentRow()) if cargo_tbl.currentRow() >= 0 else None)
    savegame_cb.currentIndexChanged.connect(
        lambda _idx: _load_selected() if not bool(state.get("updating_savegame_cb")) else None
    )
    unlock_all_btn.clicked.connect(_unlock_all_connections)
    visit_unlock_all_btn.clicked.connect(_visit_unlock_all_connections)
    apply_template_btn.clicked.connect(_apply_template)
    save_btn.clicked.connect(_save)
    close_btn.clicked.connect(dlg.reject)
    act_file_refresh.triggered.connect(lambda: _refresh_savegame_list(auto_load=False))
    act_file_load_selected.triggered.connect(_load_selected)
    act_file_open.triggered.connect(_pick_file)
    act_file_reload.triggered.connect(_reload)
    act_file_save.triggered.connect(_save)
    act_file_close.triggered.connect(dlg.reject)
    act_settings_paths.triggered.connect(_open_path_settings)
    act_help_quick.triggered.connect(
        lambda: QMessageBox.information(dlg, tr("savegame_editor.help.quick"), tr("savegame_editor.help.quick_text"))
    )
    act_help_updates.triggered.connect(lambda: _check_for_updates_popup(dlg, verbose=True))
    def _reset_program_config() -> None:
        box = QMessageBox(dlg)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle(tr("savegame_editor.help.reset_config_title"))
        box.setText(tr("savegame_editor.help.reset_config_confirm").format(path=str(CONFIG_PATH)))
        yes_btn = box.addButton(_tr_or("dlg.yes", "Yes"), QMessageBox.AcceptRole)
        box.addButton(_tr_or("dlg.no", "No"), QMessageBox.RejectRole)
        box.exec()
        if box.clickedButton() is not yes_btn:
            return
        try:
            if CONFIG_PATH.exists():
                CONFIG_PATH.unlink()
            try:
                self._cfg._d = {}
            except Exception:
                pass
            QMessageBox.information(dlg, tr("savegame_editor.title"), tr("savegame_editor.help.reset_config_done"))
        except Exception as exc:
            QMessageBox.warning(
                dlg,
                tr("savegame_editor.title"),
                tr("savegame_editor.help.reset_config_failed").format(error=str(exc)),
            )
    act_help_reset_config.triggered.connect(_reset_program_config)
    validate_btn.clicked.connect(_validate_savegame)
    def _switch_language(code: str) -> None:
        try:
            set_language(code)
            self._cfg.set("settings.language", code)
            dlg.done(2)
        except Exception:
            pass
    for code, act in lang_actions.items():
        act.triggered.connect(lambda _checked=False, c=code: _switch_language(c))
    def _apply_theme(theme_name: str) -> None:
        nonlocal current_theme
        tname = str(theme_name or "Standard").strip()
        if tname not in THEME_ORDER_SET or tname not in THEME_STYLES:
            tname = "Standard"
        if tname == current_theme:
            return
        qss = THEME_STYLES.get(tname, "")
        dlg.setUpdatesEnabled(False)
        try:
            dlg.setStyleSheet(qss)
        finally:
            dlg.setUpdatesEnabled(True)
            dlg.update()
        _apply_map_theme(tname)
        _render_known_objects_map(set(state.get("locked_ids", set()) or set()))
        _render_visited_map(set(state.get("visit_ids", set()) or set()))
        self._cfg.set("settings.theme", tname)
        current_theme = tname
        for name, act in theme_actions.items():
            try:
                act.setChecked(name == tname)
            except Exception:
                pass
    current_theme = str(self._cfg.get("settings.theme", "Standard") or "Standard").strip()
    if current_theme not in THEME_ORDER_SET or current_theme not in THEME_STYLES:
        current_theme = "Standard"
    for name, act in theme_actions.items():
        act.triggered.connect(lambda _checked=False, n=name: _apply_theme(n))
    dlg.setStyleSheet(THEME_STYLES.get(current_theme, ""))
    _apply_map_theme(current_theme)
    for name, act in theme_actions.items():
        try:
            act.setChecked(name == current_theme)
        except Exception:
            pass
    locked_view.on_system_click = _unlock_system_connections

    _refresh_savegame_list(auto_load=False)
    _set_no_savegame_state()
    _refresh_hardpoint_hint()
    app = QApplication.instance()
    if app is not None:
        splash = app.property("flatlas_savegame_splash")
        if isinstance(splash, QSplashScreen):
            splash.close()
            app.setProperty("flatlas_savegame_splash", None)
    rc = dlg.exec()
    if rc == 2:
        open_savegame_editor(self)


def run_standalone() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    icon_path = Path(__file__).with_name("images") / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    splash_path = Path(__file__).with_name("images") / "splash.png"
    if splash_path.exists():
        pix = QPixmap(str(splash_path))
        if not pix.isNull():
            splash = QSplashScreen(pix)
            splash.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            splash.show()
            app.setProperty("flatlas_savegame_splash", splash)
            app.processEvents()
    host = _SavegameEditorHost()
    _check_for_updates_popup(host)
    if not _standalone_ensure_paths(host):
        splash = app.property("flatlas_savegame_splash")
        if isinstance(splash, QSplashScreen):
            splash.close()
            app.setProperty("flatlas_savegame_splash", None)
        return 1
    host.hide()
    open_savegame_editor(host)
    host.close()
    return 0


def _standalone_ensure_paths(host: _SavegameEditorHost) -> bool:
    cfg = host._cfg
    save_path_raw = str(cfg.get("settings.savegame_path", "") or "").strip()
    game_path_raw = str(cfg.get("settings.savegame_game_path", "") or "").strip()
    save_path_obj = host._canonical_savegame_dir_from_input(save_path_raw)
    game_path_obj = host._canonical_game_dir_from_input(game_path_raw)
    save_path = str(save_path_obj).strip()
    game_path = str(game_path_obj).strip()
    save_ok = bool(save_path) and save_path_obj.exists() and save_path_obj.is_dir()
    game_ok = bool(game_path) and game_path_obj.exists() and game_path_obj.is_dir() and host._find_freelancer_exe(game_path_obj) is not None
    if save_ok:
        cfg.set("settings.savegame_path", save_path)
    if game_ok:
        cfg.set("settings.savegame_game_path", game_path)
    if save_ok and game_ok:
        return True

    dlg = QDialog(host)
    dlg.setWindowTitle(tr("savegame_editor.path_settings"))
    dlg.resize(800, 220)
    lay = QVBoxLayout(dlg)
    info = QLabel(
        tr("savegame_editor.standalone.paths_required"),
        dlg,
    )
    info.setWordWrap(True)
    lay.addWidget(info)

    form = QFormLayout()

    sg_row = QWidget(dlg)
    sg_l = QHBoxLayout(sg_row)
    sg_l.setContentsMargins(0, 0, 0, 0)
    sg_l.setSpacing(6)
    sg_default = save_path or str(host._canonical_savegame_dir_from_input(str(host._default_savegame_editor_dir())))
    sg_edit = QLineEdit(sg_default, dlg)
    sg_l.addWidget(sg_edit, 1)
    sg_browse = QPushButton(tr("welcome.browse"), dlg)
    sg_l.addWidget(sg_browse)
    form.addRow(tr("savegame_editor.path_dir"), sg_row)

    gm_row = QWidget(dlg)
    gm_l = QHBoxLayout(gm_row)
    gm_l.setContentsMargins(0, 0, 0, 0)
    gm_l.setSpacing(6)
    gm_default = game_path or str(host._canonical_game_dir_from_input(str(host._default_savegame_editor_game_path() or "")))
    gm_edit = QLineEdit(gm_default, dlg)
    gm_l.addWidget(gm_edit, 1)
    gm_browse = QPushButton(tr("welcome.browse"), dlg)
    gm_l.addWidget(gm_browse)
    form.addRow(tr("savegame_editor.game_path"), gm_row)
    lay.addLayout(form)

    buttons = QHBoxLayout()
    buttons.addStretch(1)
    ok_btn = QPushButton(tr("savegame_editor.path_apply"), dlg)
    cancel_btn = QPushButton(_tr_or("dlg.cancel", "Cancel"), dlg)
    buttons.addWidget(ok_btn)
    buttons.addWidget(cancel_btn)
    lay.addLayout(buttons)

    def _browse_save_path() -> None:
        start = sg_edit.text().strip() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(dlg, tr("welcome.browse_title"), start)
        if chosen:
            sg_edit.setText(chosen)

    def _browse_game_path() -> None:
        start = gm_edit.text().strip() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(dlg, tr("welcome.browse_title"), start)
        if chosen:
            gm_edit.setText(chosen)

    def _accept() -> None:
        sg_obj = host._canonical_savegame_dir_from_input(sg_edit.text().strip())
        gm_obj = host._canonical_game_dir_from_input(gm_edit.text().strip())
        sg = str(sg_obj).strip()
        gm = str(gm_obj).strip()
        sg_edit.setText(sg)
        gm_edit.setText(gm)
        if not sg or not sg_obj.is_dir():
            QMessageBox.warning(dlg, tr("savegame_editor.title"), tr("savegame_editor.path_dir_invalid").format(path=sg))
            return
        if not gm or not gm_obj.is_dir() or host._find_freelancer_exe(gm_obj) is None:
            QMessageBox.warning(dlg, tr("savegame_editor.title"), tr("mod_manager.launch.no_exe").format(path=gm))
            return
        cfg.set("settings.savegame_path", sg)
        cfg.set("settings.savegame_game_path", gm)
        dlg.accept()

    sg_browse.clicked.connect(_browse_save_path)
    gm_browse.clicked.connect(_browse_game_path)
    ok_btn.clicked.connect(_accept)
    cancel_btn.clicked.connect(dlg.reject)
    return dlg.exec() == int(QDialog.Accepted)


if __name__ == "__main__":
    raise SystemExit(run_standalone())
