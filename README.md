# FLAtlas Savegame Editor

Editor fuer **Freelancer**-Singleplayer-Savegames (`*.fl`).

Aktuelle Version: `v0.6.0`

## Kann was?

- Savegames oeffnen, bearbeiten und speichern
- neue Savegames erstellen
- Vanilla Freelancer und Mods nutzen
- verschluesselte `FLS1`-Saves wieder verschluesselt speichern
- automatische Backups anlegen und wiederherstellen
- Schiff, Ausruestung, Cargo, Ruf, Trent und besuchte Systeme bearbeiten
- 3D-Vorschau fuer Trent und Schiffe, wenn die Preview-Module vorhanden sind

## Starten

```bash
python -m pip install -r requirements.txt
python start_savegame_editor.py
```

Version anzeigen:

```bash
python start_savegame_editor.py --version
```

## Build

```bash
python -m pip install -r requirements-build.txt
python build.py --clean --mode onedir
```

Die fertigen Dateien landen in `dist/`.

## Konfiguration

- Windows: `%APPDATA%\fl_editor\config.json`
- Linux: `~/.config/fl_editor/config.json`

## Links

- Discord: <https://discord.gg/fY9qweRWGn>
- Issues: <https://github.com/flathack/FLAtlas---Save-Game-Editor/issues>
- Releases: <https://github.com/flathack/FLAtlas---Save-Game-Editor/releases>
