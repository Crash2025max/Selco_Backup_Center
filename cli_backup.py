import argparse
import os
import sys
import logging
from src.core.scanner import BiesseScanner
from src.core.config import ConfigManager
from src.core.backup import BackupManager

def run_auto_backup():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='backup.log')

    config = ConfigManager()
    scanner = BiesseScanner()

    auto_path = config.get("backup_paths")["auto"]
    manager = BackupManager(auto_path)

    results = scanner.scan()
    enabled_programs = config.get("programs", {})
    retention_count = config.get("retention", {}).get("count", 10)

    for name, info in results.items():
        if info["installed"] and enabled_programs.get(name, {}).get("enabled", True):
            logging.info(f"Auto-Backup für {name} gestartet...")
            success, msg = manager.create_backup(info["path"], name, is_auto=True)
            if success:
                logging.info(f"Auto-Backup für {name} erfolgreich: {msg}")
                manager.clean_old_backups(name, retention_count)
            else:
                logging.error(f"Auto-Backup für {name} FEHLGESCHLAGEN: {msg}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Run automatic backup")
    args = parser.parse_args()

    if args.auto:
        run_auto_backup()
    else:
        print("Verwenden Sie --auto zum Starten des Backups.")
