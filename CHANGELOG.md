# Changelog

Alle relevanten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

## [1.2.0] - 2026-06-03
- **Feature**: Windows Aufgabenplanung (Task Scheduler) nativ über das Programm steuerbar (`schtasks.exe`).
- **Feature**: Neues 2-Tab Layout in der UI für bessere Übersicht ("Backup & Status" | "Zeitplan").
- **Feature**: Erweiterte Test-Möglichkeiten für Auto-Backups mit minütlichen Intervallen.
- **Verbessert**: Backup Logging. Neben jedem ZIP-Archiv wird nun automatisch ein `.txt` Report mit allen gesicherten Inhalten generiert.

## [1.1.0] - 2026-06-03
- **Verbessert**: UI-Layout für die Checkboxen der Programme (Raster-Layout mit schicken Versions-Badges).
- **Behoben**: OSI-Versionserkennung liest nun korrekte UI-Version aus `Event.log`.
- **Hinzugefügt**: Dynamischer Multi-Version-Support für Optiplanning (Erkennung aller installierten Patch-Versionen).
- **Hinzugefügt**: Anzeige der App-Version in Titelleiste und Menü.

## [1.0.0] - Vorherige Arbeiten
- Implementierung des Software-Scanners (`C:\BIESSE`).
- Basis-Backup-Logik inkl. ZIP-Erstellung.
- Erster GUI-Entwurf mit CustomTkinter.

## [0.1.0] - 2023-10-27 (Initialisierung)
- Projektstruktur erstellt.
- Dokumentationsdateien (`README.md`, `CHANGELOG.md`, `TASKS.md`) hinzugefügt.
- Planung der Kernfunktionen abgeschlossen.
