# FL Atlas - Savegame Editor

Standalone editor for **Freelancer** singleplayer save files (`*.fl`).

Developed by **Aldenmar Odin - flathack**.

## Version
- Current: `v0.1.1`

## Core Features
- Open and edit Freelancer savegames with `nickname - in-game name` display where available
- Works with vanilla Freelancer and modded installs (all lookups are based on the configured game/mod files)
- Safe save workflow with automatic backup: `YourSave.fl.FLAtlasBAK`
- Savegame selector in the menu bar (shows filename + in-game save name/description)
- Story-mission protection for risky fields (system/base locked during active story mission states)

## Editor Tabs
- `Locked Gates`: view and edit locked jump gate/hole connections
- `Visited`: view known travel network and unlock all JH/JG visit entries
- `Reputation`: faction reputation table with template support (including neutral reset)
- `Customize Trent`: editable Trent body parts (`com/body/head/left hand/right hand`)
- `Ship`: ship, equipment and cargo editing with hardpoint-aware controls

## Validation and Safety
- `Check savegame` validates unknown/invalid entries (ship, equip, cargo, factions, system/base, visited)
- Integrated hardpoint auto-fix during validation for invalid equip hardpoint assignments
- Cleanup suggestions can be applied to loaded data before pressing `Save`

## UI / Theming
- Built-in themes: `Standard`, `Light`, `Dark`, `High Contrast`, `Linux KDE`
- Map rendering adapts to theme (including light map background for light themes)
- Language menu (DE/EN)

## Help Menu
- Quick help dialog
  - Includes compatibility note for vanilla FL and mods
- Manual update check
  - Returns explicit status messages (`up to date`, `check failed`, or `update available`)
- Reset program config (deletes local config file after confirmation)

## Requirements
- Python 3.10+
- PySide6
- `pefile` (for IDS/in-game name resolution from Freelancer resource DLLs)

## Start
```bash
python start_savegame_editor.py
```

The launcher can re-exec with a Python interpreter that has `pefile` available, so IDS/in-game name resolution continues to work.

## Build
This project ships with a complete PyInstaller build setup.

Files:
- `requirements-build.txt`
- `savegame_editor.spec`
- `build.py`
- `build.sh`

### Quick Build (Linux)
```bash
./build.sh onedir
```

or one-file package:
```bash
./build.sh onefile
```

### Manual Build
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
python build.py --clean --mode onedir
```

Artifacts are written to:
- `dist/`

Release bundles currently provided:
- Linux: `FLAtlas-Savegame-Editor-v0.1.1-linux-x86_64.tar.gz`
- Windows: `FLAtlas-Savegame-Editor-v0.1.1-windows-onedir.zip`

## Configuration
Local config file:
- `~/.config/fl_editor/config.json`

Relevant settings:
- `settings.savegame_path`
- `settings.savegame_game_path`
- `settings.theme`
- `settings.language`

Set paths in-app via:
- `Settings -> Path Settings`

## Notes
- Savegame changes are written only when clicking `Save`.
- Keep backups before large edits.

## Links
- Discord: https://discord.gg/RENtMMcc
- Report bugs: https://github.com/flathack/FLAtlas---Save-Game-Editor/issues or on Discord
- Releases: https://github.com/flathack/FLAtlas---Save-Game-Editor/releases
