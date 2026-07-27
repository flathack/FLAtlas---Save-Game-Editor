<h1 align="center">FLAtlas Savegame Editor</h1>

<p align="center">
  <strong>Ein sichererer Freelancer-Savegame-Editor für Singleplayer-Piloten, Mod-Nutzer und Savegame-Tests.</strong>
</p>

<p align="center">
  <strong>Deutsch</strong>
  |
  <a href="README.ru.md">Русский</a>
  |
  <a href="README.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/tag/v0.9.3">
    <img alt="Aktuelles Release" src="https://img.shields.io/badge/Aktuelles%20Release-v0.9.3-00d5ff?style=for-the-badge">
  </a>
  <a href="https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip">
    <img alt="Windows x64 herunterladen" src="https://img.shields.io/badge/Download-Windows%20x64-1f8cff?style=for-the-badge">
  </a>
  <a href="https://www.moddb.com/games/freelancer/downloads/flatlas-savegame-editor">
    <img alt="ModDB Download" src="https://img.shields.io/badge/ModDB-Freelancer%20Download-f4a300?style=for-the-badge">
  </a>
</p>

<p align="center">
  <img alt="FLAtlas Savegame Editor v0.9.3 Universumsansicht" src="assets/screenshots/flatlas-savegame-editor-v0.9.3.png">
</p>

## Download

| Build | Geeignet für | Download |
| --- | --- | --- |
| **Windows x64** | Die meisten Windows-PCs | [FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-x64.zip) |
| **Windows ARM64** | Windows-Geräte mit ARM-Prozessor | [FLAtlas-Savegame-Editor-v0.9.3-windows-arm64.zip](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/download/v0.9.3/FLAtlas-Savegame-Editor-v0.9.3-windows-arm64.zip) |
| **Release-Seite** | Changelog, Prüfsummen und ältere Builds | [GitHub Releases](https://github.com/flathack/FLAtlas---Save-Game-Editor/releases/tag/v0.9.3) |
| **ModDB-Spiegel** | Freelancer-Community-Downloadseite | [FL Atlas Savegame Editor auf ModDB](https://www.moddb.com/games/freelancer/downloads/flatlas-savegame-editor) |

Lade die ZIP-Datei herunter, entpacke sie in einen Ordner und starte den Editor aus diesem Ordner.

## Was macht das Tool?

FLAtlas Savegame Editor ist ein eigenständiger Editor für Microsoft-Freelancer-Singleplayer-Savegames (`.fl`). Er hilft beim Reparieren von Saves, beim Ändern von Fortschritt und Credits, beim Testen von Schiff-Loadouts, bei Mod-Savegame-Checks und beim sicheren Prüfen roher Savegame-Daten.

Der Editor liest Spieldaten aus deiner ausgewählten Freelancer- oder Mod-Installation. Dadurch können Systeme, Basen, Fraktionen, Schiffe, Equipment, Waren, Sprungtore und Sprunglöcher passend zu der Installation angezeigt werden, die du wirklich spielst.

## Funktionen

- Credits, Rang, Beschreibung, aktuelles System, aktuelle Basis, Spielerfraktion und Trent-Aussehen bearbeiten.
- Schiff-Setup, Kernkomponenten, Equipment-Einträge, Hardpoints, Waffen, Schilde, Thruster, Cargo und Waren ansehen und anpassen.
- Rufwerte, entdeckte Objekte, besuchte Systeme, gesperrte Gates und Freelancer-Universumsdaten bearbeiten.
- Namen und Labels aus Vanilla Freelancer, Freelancer HD Edition und Mod-Installationen auflösen.
- Savegames validieren und unbekannte oder unaufgelöste Einträge sichtbar halten, statt sie still zu verwerfen.

## Sicherheit

- Erstellt Backups, bevor Savegames geschrieben werden.
- Erhält verschlüsselte `FLS1`-Savegames beim Speichern.
- Bewahrt unbekannte Savegame-Zeilen nach Möglichkeit round-trippable auf.
- Blockiert riskante Bearbeitungen, während Freelancer läuft.
- Warnt vor Kompatibilitätsproblemen, bevor gespeichert wird.

Trotzdem ist eine eigene Sicherung wichtiger Savegames empfehlenswert, besonders vor großen oder experimentellen Änderungen.

## Hinweis zum öffentlichen Repository

Dieses GitHub-Repository ist die öffentliche Download- und Infoseite für FLAtlas Savegame Editor. Release-Dateien werden über GitHub Releases bereitgestellt. Die Entwicklung findet privat statt; dieses öffentliche Repository enthält absichtlich nicht den vollständigen Source Tree.

## Support

Fehlerberichte, Feature-Wünsche und Fragen zu Releases können über [GitHub Issues](https://github.com/flathack/FLAtlas---Save-Game-Editor/issues) eingereicht werden.
