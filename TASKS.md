# Aufgabenliste (TASKS)

Diese Liste dokumentiert den Fortschritt des Projekts und geplante Erweiterungen.

## Erledigt
- [x] Projektname definiert: "Handl Biesse Backup Manager"
- [x] Grundlegende Anforderungen geklärt
- [x] Technologiestack festgelegt (Python, CustomTkinter)
- [x] Implementierung des Software-Scanners (`C:\BIESSE`)
- [x] Basis-Backup-Logik (ZIP-Erstellung)
- [x] GUI-Entwurf mit CustomTkinter (inkl. Ladebalken für Backup-Status)
- [x] Dynamische Versionenerkennung & Multi-Version-Support (Optiplanning, OSI)
- [x] Trennung von Automatik- und Manuell-Backup (UI & Config)
- [x] Programmspezifische Backup-Regeln (LPrint, LEdit, Bopti, OSI via Archiv-Kopie, Optiplanning via Registry)
- [x] Integration der Windows Aufgabenplanung (`schtasks`) für Auto-Backups

## Nächste Schritte (Beim nächsten Mal)
- [ ] Kontrolle des OSI Backups und der dort verwendeten Pfade (Ist-Stand-Check).
- [ ] Handl Firmenlogo in die UI einpflegen.
- [ ] UI-Anpassung: Links unten die Versionsnummer nach links außen rücken und den Text "Version:" davor schreiben.

## Geplant / Offene Punkte
- [ ] Retention Policy (Löschen alter Backups) implementieren/testen
- [ ] Benachrichtigungssystem (Erfolg/Fehler)
- [ ] EXE-Erstellung mit PyInstaller
- [ ] Log-Viewer direkt in der App
- [ ] Wiederherstellungs-Assistent (späterer Zeitpunkt)

**Stand:** Version 1.2.0 (Backup-Engine & Task-Scheduler fully functional).
