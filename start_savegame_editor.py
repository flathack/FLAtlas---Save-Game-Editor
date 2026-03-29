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


def _maybe_reexec_with_pefile_python() -> None:
    # Re-exec once with a Python that has pefile so IDS/Ingame names resolve.
    if getattr(sys, "frozen", False):
        return
    if os.environ.get("FLATLAS_SKIP_REEXEC", "") == "1":
        return
    if _python_has_pefile(sys.executable):
        return
    project_root = Path(__file__).resolve().parent
    candidates = [
        project_root / ".venv" / "Scripts" / "python.exe",
        project_root / ".venv" / "bin" / "python",
        Path("/home/steven/FLEditor/.venv/bin/python"),
    ]
    for candidate in candidates:
        c = str(candidate)
        if not candidate.exists() or c == sys.executable:
            continue
        if not _python_has_pefile(c):
            continue
        env = dict(os.environ)
        env["FLATLAS_SKIP_REEXEC"] = "1"
        os.execve(c, [c, str(Path(__file__).resolve()), *sys.argv[1:]], env)


if __name__ == "__main__":
    if any(arg in ("--version", "-V") for arg in sys.argv[1:]):
        print(APP_VERSION)
        raise SystemExit(0)
    os.environ["FLATLAS_ENABLE_TRENT_PREVIEW_CALIBRATION"] = "1" if ENABLE_TRENT_PREVIEW_CALIBRATION else "0"
    _maybe_reexec_with_pefile_python()
    from fl_editor.savegame_editor import run_standalone

    raise SystemExit(run_standalone())
