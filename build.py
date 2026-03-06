#!/usr/bin/env python3
"""Build helper for FLAtlas Savegame Editor (PyInstaller)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENTRYPOINT = PROJECT_ROOT / "start_savegame_editor.py"
ICON_FILE = PROJECT_ROOT / "fl_editor" / "images" / "icon.png"


def _detect_version() -> str:
    ns: dict[str, object] = {}
    code = ENTRYPOINT.read_text(encoding="utf-8")
    exec(compile(code, str(ENTRYPOINT), "exec"), ns, ns)
    ver = str(ns.get("APP_VERSION", "") or "").strip()
    return ver or "v0.0.0"


def _ensure_clean_dirs() -> None:
    for name in ("build", "dist"):
        p = PROJECT_ROOT / name
        if p.exists():
            shutil.rmtree(p)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build FLAtlas Savegame Editor")
    ap.add_argument(
        "--mode",
        choices=("onedir", "onefile"),
        default="onedir",
        help="PyInstaller packaging mode (default: onedir)",
    )
    ap.add_argument(
        "--clean",
        action="store_true",
        help="Delete previous build/dist before building",
    )
    args = ap.parse_args()

    if not ENTRYPOINT.exists():
        print(f"Entrypoint not found: {ENTRYPOINT}", file=sys.stderr)
        return 2

    version = _detect_version()
    app_name = f"FLAtlas-Savegame-Editor-{version}"

    if args.clean:
        _ensure_clean_dirs()

    sep = ";" if sys.platform.startswith("win") else ":"
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        app_name,
        "--hidden-import",
        "pefile",
        "--add-data",
        f"{PROJECT_ROOT / 'fl_editor' / 'translations.json'}{sep}fl_editor",
        "--add-data",
        f"{PROJECT_ROOT / 'fl_editor' / 'images' / 'icon.png'}{sep}fl_editor/images",
        "--add-data",
        f"{PROJECT_ROOT / 'fl_editor' / 'images' / 'splash.png'}{sep}fl_editor/images",
        "--windowed",
    ]
    if ICON_FILE.exists():
        icon_suffix = ICON_FILE.suffix.lower()
        if (not sys.platform.startswith("win")) or icon_suffix in {".ico", ".exe"}:
            pyinstaller_cmd.extend(["--icon", str(ICON_FILE)])
    if args.mode == "onefile":
        pyinstaller_cmd.append("--onefile")
    else:
        pyinstaller_cmd.append("--onedir")
    pyinstaller_cmd.extend([str(ENTRYPOINT)])

    print("Running:", " ".join(pyinstaller_cmd))
    proc = subprocess.run(pyinstaller_cmd, cwd=str(PROJECT_ROOT))
    if proc.returncode != 0:
        return proc.returncode

    dist_path = PROJECT_ROOT / "dist"
    print(f"Build completed: {dist_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
