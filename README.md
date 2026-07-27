<h1 align="center">FLAtlas Savegame Editor</h1>

<p align="center">
  <strong>A safer Freelancer savegame editor for singleplayer pilots, mod users, and savegame testing.</strong>
</p>

<p align="center">
  <a href="README.de.md">Deutsch</a>
  |
  <a href="README.ru.md">Русский</a>
  |
  <strong>English</strong>
</p>

<p align="center">
  <a href="https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/tag/v0.9.3">
    <img alt="Latest release" src="https://img.shields.io/badge/Latest%20Release-v0.9.3-00d5ff?style=for-the-badge">
  </a>
  <a href="https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip">
    <img alt="Download Windows x64" src="https://img.shields.io/badge/Download-Windows%20x64-1f8cff?style=for-the-badge">
  </a>
  <a href="https://www.moddb.com/games/freelancer/downloads/flatlas-savegame-editor">
    <img alt="ModDB download" src="https://img.shields.io/badge/ModDB-Freelancer%20Download-f4a300?style=for-the-badge">
  </a>
</p>

<p align="center">
  <img alt="FLAtlas Savegame Editor v0.9.3 universe view" src="assets/screenshots/flatlas-savegame-editor-v0.9.3.png">
</p>

## Download

| Build | Best for | Download |
| --- | --- | --- |
| **Windows x64** | Most Windows PCs | [FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip) |
| **Windows ARM64** | ARM-based Windows devices | [FLAtlas-Savegame-Editor-v0.9.3-windows-arm64.zip](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-arm64.zip) |
| **Release page** | Changelog, checksums, older builds | [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/tag/v0.9.3) |
| **ModDB mirror** | Freelancer community download page | [FL Atlas Savegame Editor on ModDB](https://www.moddb.com/games/freelancer/downloads/flatlas-savegame-editor) |

Download the ZIP, extract it to a folder, and start the editor from the extracted folder.

## What It Does

FLAtlas Savegame Editor is a standalone editor for Microsoft Freelancer singleplayer `.fl` save files. It helps with repair work, progression edits, loadout testing, mod savegame checks, and safe inspection of raw savegame data.

The editor reads game data from your selected Freelancer or mod installation, so systems, bases, factions, ships, equipment, commodities, jump gates, and jump holes can match the install you are actually playing.

## Features

- Edit credits, rank, description, current system, current base, player faction, and Trent appearance.
- Inspect and adjust ship setup, core components, equipment entries, hardpoints, weapons, shields, thrusters, cargo, and commodities.
- Work with reputation, discovered objects, visited systems, locked gates, and Freelancer universe data.
- Resolve labels from vanilla Freelancer, Freelancer HD Edition, and modded installations.
- Validate savegames and keep unresolved or unknown rows visible instead of silently discarding them.

## Safety

- Creates backups before writing savegame changes.
- Preserves encrypted `FLS1` savegames when saving.
- Keeps unknown savegame rows round-trippable where possible.
- Blocks risky edits while Freelancer is running.
- Warns about compatibility issues before saving.

Keeping a personal backup of important savegames is still recommended, especially before large experimental edits.

## Public Repository Note

This GitHub repository is the public download and information page for FLAtlas Savegame Editor. Release assets are published through GitHub Releases. Development happens privately; this public repository intentionally does not contain the full source tree.

## Support

Bug reports, feature requests, and release questions can be submitted through [GitHub Issues](https://github.com/flathack/FLAtlas---Save-Game-Editor/issues).
