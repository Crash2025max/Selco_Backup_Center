# Handl Biesse Backup Manager

Der **Handl Biesse Backup Manager** ist ein spezialisiertes Werkzeug für die Firma Handl zur Sicherung von Maschinendaten der Biesse Selco Sägen.

## Hauptfunktionen
- **Automatischer Software-Scan:** Erkennt installierte Biesse-Programme (OSI, Optiplanning, Bopti, LEdit, LPrint) und deren Versionen.
- **Flexible Backups:** Unterstützt sowohl automatische (geplante) als auch manuelle Sicherungen.
- **Datenbank-Unterstützung:** Sichert Access-Datenbanken (OSI, Optiplanning) und bietet Schnittstellen für SQL-Backups (Bopti).
- **Speichermanagement:** Einstellbare Anzahl an zu behaltenden automatischen Sicherungen zur Platzersparnis.
- **Klare Struktur:** Backups werden nach PC-Namen, Programm und Zeitstempel benannt.
- **Benutzerfreundliche GUI:** Moderne Oberfläche entwickelt mit Python und CustomTkinter.

## Installation / Nutzung

### Für Anwender (EXE)
- Die `Handl_Biesse_Backup_Manager.exe` starten.
- Es ist keine Installation von Python erforderlich.

### Für Entwickler (Python Modus)
1. Python 3.10 oder neuer installieren.
2. Repository klonen oder Dateien kopieren.
3. Anforderungen installieren:
   ```bash
   pip install -r requirements.txt
   ```
4. Anwendung starten:
   ```bash
   python main.py
   ```
   *Unter Windows kann auch einfach die `dev_start.bat` doppelt angeklickt werden.*

## Entwickelt für
- Windows 7, 10, 11
- Python 3.x
