# FL Atlas - Savegame Editor

Standalone savegame editor for **Freelancer** save files (`*.fl`).

Developted by **Aldenmar Odin - flathack**.

## Version
- Current: `v0.1.0`

## Features
- Open, inspect and edit Freelancer singleplayer savegames
- Reputation editor with faction labels (`nickname - in-game name`)
- Map tabs for locked gates and visited jump connections
- Ship and equipment editing with hardpoint-aware filtering
- `Customize Trent` tab (voice/body/head/hands)
- Savegame description editing (in-game save display name)
- Automatic backup on save: `*.FLAtlasBAK`

## Requirements
- Python 3.10+
- PySide6
- `pefile` (for IDS/in-game name resolution from Freelancer resource DLLs)

## Start
```bash
python start_savegame_editor.py
```

The launcher auto-reexecs with a Python interpreter that has `pefile` (if available), so in-game name resolution keeps working.

## Configuration
Stored in:
- `~/.config/fl_editor/config.json`

Important paths:
- `settings.savegame_path`
- `settings.savegame_game_path`

You can set both paths in the editor via:
- `Settings -> Path Settings`

## Desktop Launcher
Use the existing `.desktop` launcher on your desktop, or create one that points to:
- `Exec=/home/steven/FLEditor/.venv/bin/python /home/steven/FLAtlas-Savegame-Editor/start_savegame_editor.py`

## Notes
- Editing system/base during active story missions can crash Freelancer. The editor protects these fields when story state is active.
- Keep backups before large edits.

## Links
- Discord: https://discord.gg/RENtMMcc
- Report bugs: https://github.com/flathack/FLAtlas/issues
