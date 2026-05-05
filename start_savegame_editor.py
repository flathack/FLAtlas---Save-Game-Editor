#!/usr/bin/env python3
"""Standalone starter for FLAtlas Savegame Editor."""

import os
import subprocess
import sys
from pathlib import Path

from fl_editor.version import APP_VERSION

ENABLE_TRENT_PREVIEW_CALIBRATION = False

def _python_has_pefile(python_exe: str) -> bool:
    try:
        proc = subprocess.run(
            [python_exe, "-c", "import pefile"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _python_has_working_qt3d(python_exe: str) -> bool:
    try:
        proc = subprocess.run(
            [
                python_exe,
                "-c",
                (
                    "import sys; "
                    "from PySide6.QtWidgets import QApplication; "
                    "app = QApplication(sys.argv); "
                    "import PySide6.Qt3DExtras as E; "
                    "ns = getattr(E, 'Qt3DExtras', E); "
                    "getattr(ns, 'Qt3DWindow')()"
                ),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
        return proc.returncode == 0
    except Exception:
        return False


def _relaunch_with_python(python_exe: str) -> None:
    env = dict(os.environ)
    env["FLATLAS_SKIP_REEXEC"] = "1"
    rc = subprocess.call([python_exe, str(Path(__file__).resolve()), *sys.argv[1:]], env=env)
    raise SystemExit(rc)


def _maybe_reexec_with_pefile_python() -> None:
    # Re-exec once if the current Python cannot resolve IDS names or cannot
    # create Qt3DWindow. The Qt3D check must happen in a subprocess because
    # broken Python/Qt combinations can crash natively.
    if getattr(sys, "frozen", False):
        return
    if os.environ.get("FLATLAS_SKIP_REEXEC", "") == "1":
        return
    current_has_pefile = _python_has_pefile(sys.executable)
    current_has_qt3d = _python_has_working_qt3d(sys.executable)
    if current_has_pefile and current_has_qt3d:
        return
    project_root = Path(__file__).resolve().parent
    candidates = [
        project_root / ".venv" / "Scripts" / "python.exe",
        project_root / ".venv" / "bin" / "python",
        project_root.parent / "FL-Lingo" / ".venv" / "Scripts" / "python.exe",
        project_root.parent / "FL-Lingo" / ".venv" / "Scripts" / "pythonw.exe",
        Path("/home/steven/FLEditor/.venv/bin/python"),
    ]
    current_exe = Path(sys.executable).resolve()
    for candidate in candidates:
        c = str(candidate)
        if not candidate.exists():
            continue
        try:
            if candidate.resolve() == current_exe:
                continue
        except Exception:
            if c == sys.executable:
                continue
        if not current_has_pefile and not _python_has_pefile(c):
            continue
        if not current_has_qt3d and not _python_has_working_qt3d(c):
            continue
        _relaunch_with_python(c)


if __name__ == "__main__":
    if any(arg in ("--version", "-V") for arg in sys.argv[1:]):
        print(APP_VERSION)
        raise SystemExit(0)
    os.environ["FLATLAS_ENABLE_TRENT_PREVIEW_CALIBRATION"] = "1" if ENABLE_TRENT_PREVIEW_CALIBRATION else "0"
    _maybe_reexec_with_pefile_python()
    from fl_editor.savegame_editor import run_standalone

    raise SystemExit(run_standalone())
