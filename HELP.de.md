# FLAtlas Savegame Editor — Hilfe

**Version:** 0.5.0  
**Entwickelt von:** Aldenmar Odin — flathack  
**GitHub:** [github.com/flathack/FLAtlas---Save-Game-Editor](https://github.com/flathack/FLAtlas---Save-Game-Editor)  
**Discord:** [discord.com/invite/RENtMMcc](https://discord.com/invite/RENtMMcc)

---

## Inhaltsverzeichnis

1. [Was ist der FLAtlas Savegame Editor?](#1-was-ist-der-flatlas-savegame-editor)
2. [Installation und Start](#2-installation-und-start)
3. [Erster Start — Pfade konfigurieren](#3-erster-start--pfade-konfigurieren)
4. [Savegame laden und speichern](#4-savegame-laden-und-speichern)
5. [Neues Savegame erstellen](#5-neues-savegame-erstellen)
6. [Seitenleiste — Allgemeine Einstellungen](#6-seitenleiste--allgemeine-einstellungen)
7. [Tab: Visited Map](#7-tab-visited-map)
8. [Tab: Reputation](#8-tab-reputation)
9. [Tab: Trent (Charakter-Aussehen)](#9-tab-trent-charakter-aussehen)
10. [Tab: Ship (Schiff)](#10-tab-ship-schiff)
    - [Ship Templates](#101-ship-templates)
    - [Core Components](#102-core-components)
    - [Equip Entries](#103-equip-entries)
    - [Cargo Entries](#104-cargo-entries)
11. [Locked Gates (Gesperrte Tore)](#11-locked-gates-gesperrte-tore)
12. [Savegame-Validierung](#12-savegame-validierung)
13. [Verschlüsselung (FLS1)](#13-verschlüsselung-fls1)
14. [Backup und Wiederherstellung](#14-backup-und-wiederherstellung)
15. [Story-Lock und Expert Mode](#15-story-lock-und-expert-mode)
16. [Kompatibilitäts-Hinweise](#16-kompatibilitäts-hinweise)
17. [Menüleiste](#17-menüleiste)
18. [Sprache und Theme](#18-sprache-und-theme)
19. [Einstellungen](#19-einstellungen)
20. [Updates](#20-updates)
21. [Häufige Fragen (FAQ)](#21-häufige-fragen-faq)
22. [Fehlerbehebung](#22-fehlerbehebung)

---

## 1. Was ist der FLAtlas Savegame Editor?

Der FLAtlas Savegame Editor ist ein eigenständiger Editor für **Freelancer**-Singleplayer-Savegames (`.fl`-Dateien). Er funktioniert mit der originalen Freelancer-Installation sowie mit Mods wie **Crossfire**, **Discovery** oder **FreelancerHD+**.

**Kernfunktionen:**

- Savegames öffnen, bearbeiten und speichern
- Schiff, Equipment, Cargo, Reputation und besuchte Systeme anpassen
- Komplette Schiffsvorlagen (Ship Templates) aus den Spieldaten anwenden
- Neue Savegames von Grund auf erstellen
- Gesperrte Jump-Verbindungen freischalten
- Automatische Backups bei jedem Speichervorgang
- Unterstützung für verschlüsselte FLS1-Saves
- Validierung des Savegames gegen die installierten Spieldaten

---

## 2. Installation und Start

### Portable Version (empfohlen)
Die fertige `.exe` aus den [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases) herunterladen und starten — keine Installation nötig.

### Python-Start (Entwicklung)
```bash
pip install -r requirements.txt
python start_savegame_editor.py
```

**Voraussetzungen:** Python 3.10+, PySide6, pefile, Pillow

---

## 3. Erster Start — Pfade konfigurieren

Beim ersten Start müssen zwei Pfade gesetzt werden:

1. **Edit → Path Settings** öffnen
2. **Savegame-Verzeichnis(se):** Der Ordner, in dem Freelancer Savegames speichert.  
   Typisch: `Dokumente\My Games\Freelancer\Accts\SinglePlayer`  
   Mehrere Verzeichnisse können mit `;` getrennt angegeben werden.
3. **Game Path:** Der Installationspfad der Freelancer-Installation (z.B. `C:\Freelancer` oder der Mod-Ordner).

Der Editor liest aus dem Game Path die Spieldaten (Schiffe, Equipment, Fraktionen usw.) und stellt sie in den ComboBoxen und Templates zur Verfügung.

**Weitere Optionen im Dialog:**
- **Preserve Encryption:** Verschlüsselte Saves bleiben beim Speichern verschlüsselt (Standard: Ein)
- **Expert Mode:** Umgeht Story-Locks und Kompatibilitätssperren (nur für erfahrene Nutzer)

---

## 4. Savegame laden und speichern

### Laden
- **Dropdown** in der Menüleiste rechts: Zeigt alle `.fl`-Dateien im konfigurierten Verzeichnis. Technische Saves (`Restart.fl`, `AutoSave.fl`, `AutoStart.fl`) werden ausgeblendet.
- **File → Open:** Öffnet ein Savegame per Dateidialog.
- **File → Open Recent:** Zeigt die letzten 8 geöffneten Dateien.
- **File → Load Selected:** Lädt das im Dropdown ausgewählte Savegame.
- **File → Reload:** Lädt das aktuelle Savegame neu von der Festplatte.

### Speichern
- **File → Save:** Zeigt eine Vorschau aller Änderungen an, dann wird gespeichert. Automatisch wird ein Backup erstellt.
- **File → Save As...:** Speichert unter einem neuen Dateinamen.

Beim Schließen mit ungespeicherten Änderungen erscheint eine Warnung mit den Optionen **Speichern**, **Verwerfen** oder **Abbrechen**.

---

## 5. Neues Savegame erstellen

Über **File → New Save...** wird ein komplett neues Savegame erzeugt:

- Name und Speicherort werden per Dialog gewählt
- Das neue Save enthält:
  - Rang 0, 2000 Credits
  - Erstes verfügbares System und erste Base
  - Erstes verfügbares Schiff mit Grundausrüstung (Power, Engine, Scanner, Tractor)
  - Trents Standard-Aussehensteile (Body, Head, Hände)
  - Standard-Reputation (Liberty Neutral)
- Das Savegame wird sofort im Editor geladen und kann weiter bearbeitet werden

---

## 6. Seitenleiste — Allgemeine Einstellungen

Die linke Seitenleiste enthält die Basisdaten des Savegames:

| Feld | Beschreibung |
|---|---|
| **Rank** | Spielerrang (0–100) |
| **Money** | Guthaben (0–999.999.999) |
| **Description** | Spielername / Beschreibung |
| **Rep Group** | Fraktionszugehörigkeit des Spielers |
| **System** | Aktuelles System — filtert die verfügbaren Basen |
| **Base** | Aktuelle Basis innerhalb des gewählten Systems |

Unterhalb befindet sich der **Check Savegame**-Button für die Validierung.

---

## 7. Tab: Visited Map

Die Visited Map zeigt eine interaktive Karte aller Freelancer-Systeme:

- **Grau:** Nicht besucht / unbekannt
- **Grün:** Besucht
- **Rot:** Aktuelles System des Spielers

Verbindungslinien zwischen Systemen zeigen den Zustand der Jump-Verbindungen (inaktiv, gesperrt, besucht).

### Aktionen

| Button | Funktion |
|---|---|
| **Unlock All** | Entsperrt alle gesperrten Jump-Verbindungen |
| **Mark all JH/JG** | Markiert alle Jumpholes und Jumpgates sowie deren Systeme als besucht |
| **Reveal Everything** | Markiert ALLE Einträge als besucht — Systeme, Objekte, Zonen |

**Rechtsklick** auf einen System-Knoten zeigt ein Kontextmenü zum Entsperren einzelner Verbindungen.

**View → Center Current System** zentriert die Karte auf das aktuelle System.

---

## 8. Tab: Reputation

Die Reputationstabelle zeigt alle Fraktionen mit ihrem Reputationswert:

- **Spalte Faction:** Fraktionsname
- **Spalte Rep:** Reputationswert (-0.91 bis +0.91) als numerisches Eingabefeld
- **Farbcodierung:** Rot für feindlich (< -0.61), Grün für freundlich (> +0.61)
- **Filter:** Suchfeld zum schnellen Finden von Fraktionen

### Reputation Templates

Das **Template-Dropdown** bietet vorgefertigte Reputationsprofile an. Bei Auswahl und Klick auf **Apply** werden die Reputationswerte aller kompatiblen Fraktionen überschrieben. Inkompatible Fraktionseinträge (z.B. aus Mods, die nicht zur aktuellen Installation passen) bleiben unverändert.

---

## 9. Tab: Trent (Charakter-Aussehen)

Hier werden die Körperteile des Spielercharakters Trent bearbeitet. Es gibt 8 ComboBoxen:

**Kommissionierte Teile** (für Zwischensequenzen):
- Com Body
- Com Head
- Com Left Hand
- Com Right Hand

**Standard-Teile** (im Spiel):
- Body
- Head
- Left Hand
- Right Hand

**Hinweis:** Wenn das Savegame einen `costume`- oder `com_costume`-Eintrag enthält (z.B. aus einer aktiven Story-Mission), wird der Trent-Tab **gesperrt**, um die Originalwerte zu schützen. Im Expert Mode kann diese Sperre umgangen werden.

---

## 10. Tab: Ship (Schiff)

### Schiffsauswahl

Die **Ship Archetype**-ComboBox oben im Tab wählt den Schiffstyp. Die ComboBox ist editierbar und durchsuchbar.

### 10.1 Ship Templates

Das **Ship Template**-Dropdown listet alle verfügbaren Schiffskonfigurationen aus den Spieldaten (`goods.ini`). Jedes Template entspricht einem `_package`-Eintrag und enthält:

- Schiffstyp
- Alle Core Components (Power, Engine, Scanner, Tractor)
- Alle Equip-Einträge (Schild, Waffen, Lights, Contrails usw.)

**Apply** übernimmt die komplette Konfiguration auf einmal — Ship Archetype, Core Components und alle Equipment-Einträge werden ersetzt.

### 10.2 Core Components

Der Subtab **Core Components** enthält die Kernausrüstung des Schiffs:

| Feld | Beschreibung |
|---|---|
| **Power** | Kraftwerk (Energieversorgung) |
| **Engine** | Antrieb |
| **Scanner** | Scanner |
| **Tractor** | Traktorstrahl |
| **Cloak** | Tarnvorrichtung (nur sichtbar, wenn ein Cloak-Mod installiert ist) |

### 10.3 Equip Entries

Der Subtab **Equip Entries** zeigt die Hardpoint-Ausrüstung in einer Tabelle:

- **Item:** Equipment-Auswahl (editierbare ComboBox)
- **Hardpoint:** Zugewiesener Hardpoint am Schiff

| Button | Funktion |
|---|---|
| **Add Equip** | Fügt eine neue leere Zeile hinzu |
| **Remove Selected** | Entfernt die markierte(n) Zeile(n) |
| **Autofix Hardpoints** | Korrigiert automatisch ungültige Hardpoint-Zuweisungen |

Das **Filter-Feld** schränkt die Anzeige auf passende Einträge ein.

### 10.4 Cargo Entries

Der Subtab **Cargo Entries** verwaltet den Frachtraum:

- **Shield Batteries:** Anzahl (0–9999)
- **Repair Kits:** Anzahl (0–9999)
- **Cargo-Tabelle:** Item + Menge

| Button | Funktion |
|---|---|
| **Add Cargo** | Fügt einen neuen Fracht-Eintrag hinzu |
| **Remove Selected** | Entfernt die markierte(n) Zeile(n) |

---

## 11. Locked Gates (Gesperrte Tore)

Freelancer sperrt bestimmte Jump-Verbindungen über `locked_gate`-Einträge im Savegame. Der Editor zeigt diese auf der Karte als farblich markierte Verbindungslinien.

- **Unlock All** auf der Karte entsperrt alle Verbindungen auf einmal
- **Rechtsklick** auf ein System erlaubt das selektive Entsperren einzelner Verbindungen
- `npc_locked_gate`-Einträge (NPC-Sperren) werden getrennt behandelt und nicht versehentlich überschrieben

---

## 12. Savegame-Validierung

Über **Tools → Check Savegame** oder den **Check Savegame**-Button in der Seitenleiste wird das geladene Savegame gegen die Spieldaten validiert:

**Geprüft werden:**
- Schiff (ship_archetype) — existiert das Schiff in den Spieldaten?
- Equipment (equip) — sind alle Gegenstände bekannt?
- Cargo — sind alle Frachtgüter bekannt?
- Fraktionen (house, rep_group) — existieren alle Fraktionen?
- System und Base — sind die Ortsdaten gültig?
- Visit-Einträge — verweisen alle visit-IDs auf bekannte Objekte?

Ungültige Einträge werden aufgelistet. Der **Cleanup**-Button kann erkannte ungültige Einträge automatisch entfernen.

---

## 13. Verschlüsselung (FLS1)

Freelancer-Savegames können mit dem FLS1/GENE-Cipher verschlüsselt sein.

- Der Editor erkennt verschlüsselte Saves automatisch
- Verschlüsselte Saves werden entschlüsselt, bearbeitet und — wenn die Option **Preserve Encryption** aktiv ist — beim Speichern wieder verschlüsselt
- Der Verschlüsselungsstatus wird in der Statusleiste angezeigt
- Die Option kann unter **Edit → Path Settings** geändert werden

---

## 14. Backup und Wiederherstellung

Bei jedem Speichern erstellt der Editor automatisch Backups:

- **Aktuelles Backup:** `DeinSave.fl.FLAtlasBAK`
- **Zeitstempel-Backup:** `DeinSave.fl.FLAtlasBAK.YYYYMMDD_HHMMSS`

### Backup wiederherstellen

1. **File → Restore Backup** öffnen
2. Links: Liste aller verfügbaren Backups
3. Rechts: Diff-Vergleich zwischen gewähltem Backup und aktuellem Save
4. **Restore** stellt das gewählte Backup wieder her — der aktuelle Stand wird vorher als neues Backup gesichert

**Hinweis:** Backup-Dateien wachsen mit der Zeit. Alte Snapshots können manuell gelöscht werden.

---

## 15. Story-Lock und Expert Mode

### Story-Lock

Wenn im Savegame eine aktive Story-Mission erkannt wird (`[StoryInfo]` mit aktiver `missionnum`), werden bestimmte Felder gesperrt:

- **System** und **Base** können nicht geändert werden (da Story-Missionen ortsbezogen sind)
- Der **Trent**-Tab wird gesperrt (Kostüm durch Story vorgegeben)
- Eine Warnmeldung zeigt den Story-Lock-Status an

### Expert Mode

Aktivierbar unter **Edit → Path Settings → Expert Mode**.

Im Expert Mode werden alle Sicherheitsrestriktionen umgangen:
- Story-Locks werden ignoriert
- Kompatibilitätssperren werden aufgehoben
- Inkompatible Einträge können bearbeitet werden

**Achtung:** Falsche Änderungen im Expert Mode können das Savegame beschädigen oder Abstürze im Spiel verursachen.

---

## 16. Kompatibilitäts-Hinweise

Wenn ein Savegame Einträge enthält, die nicht zur konfigurierten Freelancer-Installation passen (z.B. Mod-Items in einer Vanilla-Installation), zeigt der Editor Warnungen:

- Eine **orangefarbene Warnung** in der Statusleiste
- Inkompatible Einträge werden als **gesperrte, schreibgeschützte Zeilen** dargestellt
- Diese Einträge bleiben beim Speichern unverändert erhalten
- Numerische IDs, die keinem bekannten Item zugeordnet werden können, bleiben als Zahlen sichtbar

---

## 17. Menüleiste

| Menü | Einträge |
|---|---|
| **File** | New Save, Open, Open Recent, Load Selected, Reload, Save, Save As, Restore Backup, Refresh List, Close |
| **Edit** | Path Settings |
| **View** | Center Current System, Language, Theme |
| **Tools** | Check Savegame, Reset Config |
| **Help** | Quick Help, Online Help (Wiki), Check for Updates, About |

---

## 18. Sprache und Theme

### Sprache wechseln
**View → Language** bietet: Deutsch, English, Русский, Español, Français

### Theme wechseln
**View → Theme** bietet: Light, Dark

Beide Einstellungen werden sofort angewendet und in der Konfiguration gespeichert.

---

## 19. Einstellungen

Die Konfigurationsdatei liegt unter:
- **Windows:** `%APPDATA%\fl_editor\config.json`
- **Linux:** `~/.config/fl_editor/config.json`

| Einstellung | Beschreibung |
|---|---|
| `settings.savegame_path` | Savegame-Verzeichnis(se) |
| `settings.savegame_game_path` | Freelancer-Installationspfad |
| `settings.savegame_recent_files` | Zuletzt geöffnete Dateien (max. 8) |
| `settings.savegame_preserve_encryption` | FLS1-Verschlüsselung beibehalten |
| `settings.theme` | Aktuelles Theme (light/dark) |
| `settings.language` | Aktuelle Sprache |

**Tools → Reset Config** setzt alle Einstellungen auf die Standardwerte zurück.

---

## 20. Updates

**Help → Check for Updates** prüft die [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases) auf neuere Versionen.

Mögliche Ergebnisse:
- **Aktuell:** Keine neuere Version verfügbar
- **Update verfügbar:** Link zum Download der neuen Version
- **Voraus:** Installierte Version ist neuer als das letzte Release (z.B. Entwicklungsversion)
- **Fehler:** Netzwerkproblem oder API nicht erreichbar

### Auto-Updater

Wenn der Editor als gepackte Windows-Version (.exe) läuft und ein passendes Update-Paket im Release vorhanden ist, erscheint im Update-Dialog zusätzlich der Button **"Update installieren"**.

Der Auto-Update-Vorgang:
1. Das Update wird heruntergeladen (Fortschrittsanzeige)
2. Das Archiv wird entpackt
3. Der Updater-Prozess (`FLEditorUpdater.exe`) wird gestartet
4. Der Editor wird beendet
5. Der Updater wartet bis der Editor geschlossen ist, kopiert die neuen Dateien und startet den Editor neu

**Hinweis:** Bei der Python-Entwicklungsversion steht nur der manuelle Download über "Open Download" zur Verfügung.

**Help → Online Help (Wiki)** öffnet die [Online-Hilfe](https://github.com/flathack/FLAtlas---Save-Game-Editor/wiki) im Browser.

---

## 21. Häufige Fragen (FAQ)

**F: Ich kann System oder Base nicht ändern.**  
A: Es ist wahrscheinlich eine Story-Mission aktiv. Beende die Mission im Spiel oder aktiviere den Expert Mode unter **Edit → Path Settings**.

**F: Der Trent-Tab ist komplett gesperrt.**  
A: Das Savegame enthält einen `costume`- oder `com_costume`-Eintrag, der vom Editor geschützt wird. Im Expert Mode ist die Bearbeitung möglich.

**F: Manche Einträge zeigen nur Zahlen statt Namen.**  
A: Die zugehörigen Spieldaten fehlen oder der Game Path zeigt auf eine andere Installation. Prüfe den Pfad unter **Edit → Path Settings**.

**F: Mein Savegame ist verschlüsselt — kann ich es trotzdem bearbeiten?**  
A: Ja, der Editor entschlüsselt FLS1-Saves automatisch. Mit der Option **Preserve Encryption** wird die Verschlüsselung beim Speichern wiederhergestellt.

**F: Das Ship Template-Dropdown ist leer.**  
A: Der Game Path ist nicht korrekt gesetzt oder die `goods.ini` enthält keine `_package`-Einträge. Prüfe den Pfad unter **Edit → Path Settings**.

**F: Kann ich ein Savegame aus einer anderen Mod laden?**  
A: Ja, aber Einträge die nicht zur konfigurierten Installation passen werden als inkompatibel markiert und können nicht bearbeitet werden. Sie bleiben beim Speichern erhalten.

**F: Wo finde ich meine Savegames?**  
A: Typische Pfade:
- Vanilla: `Dokumente\My Games\Freelancer\Accts\SinglePlayer`
- FreelancerHD+: `Dokumente\My Games\FreelancerHDE\Accts\SinglePlayer`
- Crossfire: `Dokumente\My Games\Crossfire`
- Discovery: `Dokumente\My Games\Discovery`

---

## 22. Fehlerbehebung

**Editor startet nicht:**
- Python 3.10+ und PySide6 müssen installiert sein
- Bei der portablen Version: Antivirus-Ausnahme für die `.exe` hinzufügen

**Spieldaten werden nicht geladen:**
- Game Path prüfen — er muss auf den Hauptordner der Freelancer-Installation zeigen (mit `DATA`- und `EXE`-Unterordnern)

**Save lässt sich nicht öffnen:**
- Dateiformat prüfen — nur `.fl`-Dateien werden unterstützt
- Datei ist möglicherweise beschädigt — ggf. aus dem Backup-Ordner wiederherstellen

**Änderungen werden im Spiel nicht übernommen:**
- Sicherstellen, dass das richtige Savegame gespeichert wurde
- Bei verschlüsselten Saves: **Preserve Encryption** muss aktiv sein

**Backup wiederherstellen schlägt fehl:**
- Die Backup-Dateien (`.FLAtlasBAK`) müssen im selben Ordner wie das Original liegen

---

*FLAtlas Savegame Editor v0.2.0 — Aldenmar Odin / flathack*
