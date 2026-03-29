# FLAtlas Savegame Editor — Help

**Version:** 0.5.0  
**Developed by:** Aldenmar Odin — flathack  
**GitHub:** [github.com/flathack/FLAtlas---Save-Game-Editor](https://github.com/flathack/FLAtlas---Save-Game-Editor)  
**Discord:** [discord.com/invite/RENtMMcc](https://discord.com/invite/RENtMMcc)

---

## Table of Contents

1. [What is the FLAtlas Savegame Editor?](#1-what-is-the-flatlas-savegame-editor)
2. [Installation and Startup](#2-installation-and-startup)
3. [First Launch — Configuring Paths](#3-first-launch--configuring-paths)
4. [Loading and Saving](#4-loading-and-saving)
5. [Creating a New Save](#5-creating-a-new-save)
6. [Sidebar — General Settings](#6-sidebar--general-settings)
7. [Tab: Visited Map](#7-tab-visited-map)
8. [Tab: Reputation](#8-tab-reputation)
9. [Tab: Trent (Character Appearance)](#9-tab-trent-character-appearance)
10. [Tab: Ship](#10-tab-ship)
    - [Ship Templates](#101-ship-templates)
    - [Core Components](#102-core-components)
    - [Equip Entries](#103-equip-entries)
    - [Cargo Entries](#104-cargo-entries)
11. [Locked Gates](#11-locked-gates)
12. [Savegame Validation](#12-savegame-validation)
13. [Encryption (FLS1)](#13-encryption-fls1)
14. [Backup and Restore](#14-backup-and-restore)
15. [Story Lock and Expert Mode](#15-story-lock-and-expert-mode)
16. [Compatibility Notes](#16-compatibility-notes)
17. [Menu Bar](#17-menu-bar)
18. [Language and Theme](#18-language-and-theme)
19. [Settings](#19-settings)
20. [Updates](#20-updates)
21. [Frequently Asked Questions (FAQ)](#21-frequently-asked-questions-faq)
22. [Troubleshooting](#22-troubleshooting)

---

## 1. What is the FLAtlas Savegame Editor?

The FLAtlas Savegame Editor is a standalone editor for **Freelancer** singleplayer save files (`.fl` files). It works with the original Freelancer installation as well as mods like **Crossfire**, **Discovery**, or **FreelancerHD+**.

**Key Features:**

- Open, edit, and save Freelancer savegames
- Modify ship, equipment, cargo, reputation, and visited systems
- Apply complete ship templates from game data
- Create new savegames from scratch
- Unlock locked jump connections
- Automatic backups on every save
- Support for encrypted FLS1 saves
- Validate savegame contents against installed game data

---

## 2. Installation and Startup

### Portable Version (recommended)
Download the ready-to-use `.exe` from [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases) and run it — no installation required.

### Python Start (development)
```bash
pip install -r requirements.txt
python start_savegame_editor.py
```

**Requirements:** Python 3.10+, PySide6, pefile, Pillow

---

## 3. First Launch — Configuring Paths

On first launch, two paths must be configured:

1. Open **Edit → Path Settings**
2. **Savegame Directory/Directories:** The folder where Freelancer stores save files.  
   Typical: `Documents\My Games\Freelancer\Accts\SinglePlayer`  
   Multiple directories can be separated with `;`.
3. **Game Path:** The installation path of the Freelancer installation (e.g. `C:\Freelancer` or the mod folder).

The editor reads game data (ships, equipment, factions, etc.) from the Game Path and populates the combo boxes and templates accordingly.

**Additional options in the dialog:**
- **Preserve Encryption:** Encrypted saves remain encrypted when saved (default: On)
- **Expert Mode:** Bypasses story locks and compatibility restrictions (advanced users only)

---

## 4. Loading and Saving

### Loading
- **Dropdown** in the menu bar (right side): Shows all `.fl` files in the configured directory. Technical saves (`Restart.fl`, `AutoSave.fl`, `AutoStart.fl`) are hidden.
- **File → Open:** Opens a savegame via file dialog.
- **File → Open Recent:** Shows the last 8 opened files.
- **File → Load Selected:** Loads the savegame selected in the dropdown.
- **File → Reload:** Reloads the current savegame from disk.

### Saving
- **File → Save:** Shows a preview of all changes, then saves. A backup is created automatically.
- **File → Save As...:** Saves under a new file name.

When closing with unsaved changes, a warning appears with the options **Save**, **Discard**, or **Cancel**.

---

## 5. Creating a New Save

Via **File → New Save...** a completely new savegame is created:

- Name and save location are chosen via a file dialog
- The new save contains:
  - Rank 0, 2000 credits
  - First available system and base
  - First available ship with basic equipment (power, engine, scanner, tractor)
  - Trent's default appearance parts (body, head, hands)
  - Default reputation (Liberty Neutral)
- The savegame is immediately loaded in the editor and can be further edited

---

## 6. Sidebar — General Settings

The left sidebar contains the basic savegame data:

| Field | Description |
|---|---|
| **Rank** | Player rank (0–100) |
| **Money** | Credits (0–999,999,999) |
| **Description** | Player name / description |
| **Rep Group** | Player's faction affiliation |
| **System** | Current system — filters available bases |
| **Base** | Current base within the selected system |

Below is the **Check Savegame** button for validation.

---

## 7. Tab: Visited Map

The Visited Map displays an interactive map of all Freelancer systems:

- **Gray:** Not visited / unknown
- **Green:** Visited
- **Red:** Player's current system

Connection lines between systems indicate the state of jump connections (inactive, locked, visited).

### Actions

| Button | Function |
|---|---|
| **Unlock All** | Unlocks all locked jump connections |
| **Mark all JH/JG** | Marks all jumpholes, jumpgates, and their systems as visited |
| **Reveal Everything** | Marks ALL entries as visited — systems, objects, zones |

**Right-click** on a system node shows a context menu for unlocking individual connections.

**View → Center Current System** centers the map on the current system.

---

## 8. Tab: Reputation

The reputation table shows all factions with their reputation value:

- **Faction column:** Faction name
- **Rep column:** Reputation value (-0.91 to +0.91) as a numeric input
- **Color coding:** Red for hostile (< -0.61), Green for friendly (> +0.61)
- **Filter:** Search field for quickly finding factions

### Reputation Templates

The **Template dropdown** offers pre-built reputation profiles. Selecting one and clicking **Apply** overwrites the reputation values for all compatible factions. Incompatible faction entries (e.g. from mods that don't match the current installation) remain unchanged.

---

## 9. Tab: Trent (Character Appearance)

This tab manages the body parts of the player character Trent. There are 8 combo boxes:

**Commissioned parts** (for cutscenes):
- Com Body
- Com Head
- Com Left Hand
- Com Right Hand

**Standard parts** (in-game):
- Body
- Head
- Left Hand
- Right Hand

**Note:** If the savegame contains a `costume` or `com_costume` entry (e.g. from an active story mission), the Trent tab is **locked** to protect the original values. Expert Mode can bypass this lock.

---

## 10. Tab: Ship

### Ship Selection

The **Ship Archetype** combo box at the top of the tab selects the ship type. The combo box is editable and searchable.

### 10.1 Ship Templates

The **Ship Template** dropdown lists all available ship configurations from the game data (`goods.ini`). Each template corresponds to a `_package` entry and includes:

- Ship type
- All core components (power, engine, scanner, tractor)
- All equip entries (shield, weapons, lights, contrails, etc.)

**Apply** transfers the complete configuration at once — ship archetype, core components, and all equipment entries are replaced.

### 10.2 Core Components

The **Core Components** subtab contains the ship's core equipment:

| Field | Description |
|---|---|
| **Power** | Powerplant (energy supply) |
| **Engine** | Engine (propulsion) |
| **Scanner** | Scanner |
| **Tractor** | Tractor beam |
| **Cloak** | Cloaking device (only visible if a cloak mod is installed) |

### 10.3 Equip Entries

The **Equip Entries** subtab shows hardpoint equipment in a table:

- **Item:** Equipment selection (editable combo box)
- **Hardpoint:** Assigned hardpoint on the ship

| Button | Function |
|---|---|
| **Add Equip** | Adds a new empty row |
| **Remove Selected** | Removes the selected row(s) |
| **Autofix Hardpoints** | Automatically corrects invalid hardpoint assignments |

The **Filter field** narrows the display to matching entries.

### 10.4 Cargo Entries

The **Cargo Entries** subtab manages the cargo hold:

- **Shield Batteries:** Count (0–9999)
- **Repair Kits:** Count (0–9999)
- **Cargo table:** Item + Amount

| Button | Function |
|---|---|
| **Add Cargo** | Adds a new cargo entry |
| **Remove Selected** | Removes the selected row(s) |

---

## 11. Locked Gates

Freelancer locks certain jump connections via `locked_gate` entries in the savegame. The editor displays these as color-coded connection lines on the map.

- **Unlock All** on the map unlocks all connections at once
- **Right-click** on a system allows selectively unlocking individual connections
- `npc_locked_gate` entries (NPC locks) are handled separately and not accidentally overwritten

---

## 12. Savegame Validation

Via **Tools → Check Savegame** or the **Check Savegame** button in the sidebar, the loaded savegame is validated against game data:

**Checks performed:**
- Ship (ship_archetype) — does the ship exist in the game data?
- Equipment (equip) — are all items known?
- Cargo — are all commodities known?
- Factions (house, rep_group) — do all factions exist?
- System and Base — are the location values valid?
- Visit entries — do all visit IDs reference known objects?

Invalid entries are listed. The **Cleanup** button can automatically remove detected invalid entries.

---

## 13. Encryption (FLS1)

Freelancer savegames can be encrypted with the FLS1/GENE cipher.

- The editor automatically detects encrypted saves
- Encrypted saves are decrypted for editing and — if the **Preserve Encryption** option is active — re-encrypted when saving
- The encryption status is shown in the status bar
- The option can be changed under **Edit → Path Settings**

---

## 14. Backup and Restore

On every save, the editor automatically creates backups:

- **Current backup:** `YourSave.fl.FLAtlasBAK`
- **Timestamped backup:** `YourSave.fl.FLAtlasBAK.YYYYMMDD_HHMMSS`

### Restoring a Backup

1. Open **File → Restore Backup**
2. Left side: List of all available backups
3. Right side: Diff comparison between selected backup and current save
4. **Restore** restores the selected backup — the current state is saved as a new backup first

**Note:** Backup files grow over time. Old snapshots can be deleted manually.

---

## 15. Story Lock and Expert Mode

### Story Lock

When an active story mission is detected in the savegame (`[StoryInfo]` with active `missionnum`), certain fields are locked:

- **System** and **Base** cannot be changed (story missions are location-dependent)
- The **Trent** tab is locked (costume dictated by story)
- A warning message shows the story lock status

### Expert Mode

Activatable under **Edit → Path Settings → Expert Mode**.

In Expert Mode, all safety restrictions are bypassed:
- Story locks are ignored
- Compatibility locks are lifted
- Incompatible entries can be edited

**Warning:** Incorrect changes in Expert Mode can corrupt the savegame or cause crashes in-game.

---

## 16. Compatibility Notes

When a savegame contains entries that don't match the configured Freelancer installation (e.g. mod items in a vanilla installation), the editor shows warnings:

- An **orange warning** in the status bar
- Incompatible entries are displayed as **locked, read-only rows**
- These entries are preserved unchanged when saving
- Numeric IDs that cannot be mapped to a known item remain visible as numbers

---

## 17. Menu Bar

| Menu | Items |
|---|---|
| **File** | New Save, Open, Open Recent, Load Selected, Reload, Save, Save As, Restore Backup, Refresh List, Close |
| **Edit** | Path Settings |
| **View** | Center Current System, Language, Theme |
| **Tools** | Check Savegame, Reset Config |
| **Help** | Quick Help, Online Help (Wiki), Check for Updates, About |

---

## 18. Language and Theme

### Changing Language
**View → Language** offers: Deutsch, English, Русский, Español, Français

### Changing Theme
**View → Theme** offers: Light, Dark

Both settings are applied immediately and saved to the configuration.

---

## 19. Settings

The configuration file is located at:
- **Windows:** `%APPDATA%\fl_editor\config.json`
- **Linux:** `~/.config/fl_editor/config.json`

| Setting | Description |
|---|---|
| `settings.savegame_path` | Savegame directory/directories |
| `settings.savegame_game_path` | Freelancer installation path |
| `settings.savegame_recent_files` | Recently opened files (max. 8) |
| `settings.savegame_preserve_encryption` | Preserve FLS1 encryption |
| `settings.theme` | Current theme (light/dark) |
| `settings.language` | Current language |

**Tools → Reset Config** resets all settings to their defaults.

---

## 20. Updates

**Help → Check for Updates** checks [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases) for newer versions.

Possible results:
- **Up to date:** No newer version available
- **Update available:** Link to download the new version
- **Ahead:** Installed version is newer than the latest release (e.g. development build)
- **Error:** Network issue or API unreachable

### Auto-Updater

When the editor runs as a packaged Windows version (.exe) and a matching update package is available in the release, the update dialog shows an additional **"Update installieren"** (Install Update) button.

The auto-update process:
1. The update is downloaded (with progress bar)
2. The archive is extracted
3. The updater process (`FLEditorUpdater.exe`) is launched
4. The editor closes
5. The updater waits for the editor to shut down, copies the new files, and restarts the editor

**Note:** When running from Python source, only the manual download via "Open Download" is available.

**Help → Online Help (Wiki)** opens the [online help](https://github.com/flathack/FLAtlas---Save-Game-Editor/wiki) in your browser.

---

## 21. Frequently Asked Questions (FAQ)

**Q: I can't change System or Base.**  
A: A story mission is likely active. Complete the mission in-game or enable Expert Mode under **Edit → Path Settings**.

**Q: The Trent tab is completely locked.**  
A: The savegame contains a `costume` or `com_costume` entry that is protected by the editor. Expert Mode allows editing.

**Q: Some entries show only numbers instead of names.**  
A: The corresponding game data is missing or the Game Path points to a different installation. Check the path under **Edit → Path Settings**.

**Q: My savegame is encrypted — can I still edit it?**  
A: Yes, the editor automatically decrypts FLS1 saves. With the **Preserve Encryption** option, encryption is restored when saving.

**Q: The Ship Template dropdown is empty.**  
A: The Game Path is not set correctly or the `goods.ini` doesn't contain `_package` entries. Check the path under **Edit → Path Settings**.

**Q: Can I load a savegame from another mod?**  
A: Yes, but entries that don't match the configured installation will be marked as incompatible and cannot be edited. They are preserved when saving.

**Q: Where do I find my savegames?**  
A: Typical paths:
- Vanilla: `Documents\My Games\Freelancer\Accts\SinglePlayer`
- FreelancerHD+: `Documents\My Games\FreelancerHDE\Accts\SinglePlayer`
- Crossfire: `Documents\My Games\Crossfire`
- Discovery: `Documents\My Games\Discovery`

---

## 22. Troubleshooting

**Editor won't start:**
- Python 3.10+ and PySide6 must be installed
- For the portable version: Add an antivirus exception for the `.exe`

**Game data doesn't load:**
- Check the Game Path — it must point to the main folder of the Freelancer installation (with `DATA` and `EXE` subfolders)

**Save file won't open:**
- Check the file format — only `.fl` files are supported
- The file may be corrupted — try restoring from the backup folder

**Changes are not reflected in-game:**
- Make sure the correct savegame was saved
- For encrypted saves: **Preserve Encryption** must be active

**Backup restore fails:**
- The backup files (`.FLAtlasBAK`) must be in the same folder as the original

---

*FLAtlas Savegame Editor v0.2.0 — Aldenmar Odin / flathack*
