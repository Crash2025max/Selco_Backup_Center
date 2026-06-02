import os
import zipfile
import datetime
import platform
import logging
import shutil

class BackupManager:
    def __init__(self, target_base_path):
        self.target_base_path = target_base_path
        self.pc_name = platform.node()

    def create_backup(self, source_path, program_name, is_auto=False, custom_func=None):
        """
        Creates a ZIP backup of the given source path.
        If custom_func is provided, it executes that instead of default zipping.
        """
        if custom_func:
            return custom_func(self, source_path, program_name, is_auto)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_type = "Auto" if is_auto else "Manuell"

        # Format: [PC-NAME]_[PROGRAMM]_[TYP]_[DATUM]_[UHRZEIT].zip
        filename = f"{self.pc_name}_{program_name}_{backup_type}_{timestamp}.zip"

        if not os.path.exists(self.target_base_path):
            os.makedirs(self.target_base_path)

        target_file = os.path.join(self.target_base_path, filename)

        try:
            with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(source_path):
                    zipf.write(source_path, os.path.basename(source_path))
                else:
                    for root, dirs, files in os.walk(source_path):
                        # Avoid backing up the backup folder itself if it's inside source
                        if self.target_base_path in os.path.abspath(root):
                            continue

                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_path)
                            zipf.write(file_path, arcname)

            logging.info(f"Backup erfolgreich erstellt: {target_file}")
            return True, target_file
        except Exception as e:
            logging.error(f"Fehler bei Backup-Erstellung: {e}")
            return False, str(e)

    def verify_backup(self, zip_path):
        """Simple integrity check of the zip file."""
        try:
            if not os.path.exists(zip_path):
                return False
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # testzip() returns None if no errors are found
                return zipf.testzip() is None
        except Exception as e:
            logging.error(f"Integritätsprüfung fehlgeschlagen für {zip_path}: {e}")
            return False

    def clean_old_backups(self, program_name, keep_count):
        """Removes old auto backups, keeps manual ones."""
        if keep_count <= 0:
            return

        backups = []
        for f in os.listdir(self.target_base_path):
            # Only consider auto backups for deletion
            if f.startswith(f"{self.pc_name}_{program_name}_Auto_") and f.endswith(".zip"):
                path = os.path.join(self.target_base_path, f)
                backups.append((path, os.path.getmtime(path)))

        # Sort by modification time (oldest first)
        backups.sort(key=lambda x: x[1])

        if len(backups) > keep_count:
            to_delete = backups[:-keep_count]
            for path, _ in to_delete:
                try:
                    os.remove(path)
                    logging.info(f"Altes Backup gelöscht: {path}")
                except Exception as e:
                    logging.error(f"Fehler beim Löschen von {path}: {e}")

if __name__ == "__main__":
    # Test block
    logging.basicConfig(level=logging.INFO)
    # ... test logic ...
