import os
import zipfile
import datetime
import platform
import logging
import shutil
import winreg
from src.core.backup_rules import get_backup_rule

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

        txt_filename = filename.replace('.zip', '.txt')
        txt_target_file = os.path.join(self.target_base_path, txt_filename)

        backed_up_files = []

        rule = get_backup_rule(program_name)
        is_selective = rule["type"] == "selective"

        try:
            if rule["type"] == "copy_latest_zip":
                archive_dir = os.path.join(source_path, rule["folder"])
                
                # OSI specific: Check if ZipDir is overridden in Options.txt
                options_path = os.path.join(source_path, "Options.txt")
                if os.path.exists(options_path):
                    try:
                        with open(options_path, 'r', encoding='latin-1', errors='ignore') as f:
                            for line in f:
                                if line.startswith("ZipDir\t") or line.startswith("ZipDir="):
                                    parts = line.split('\t') if '\t' in line else line.split('=')
                                    if len(parts) > 1:
                                        potential_path = parts[1].strip()
                                        if os.path.isdir(potential_path):
                                            archive_dir = potential_path
                                        break
                    except Exception as e:
                        logging.warning(f"Konnte Options.txt nicht lesen: {e}")

                if not os.path.exists(archive_dir):
                    return False, f"Archiv-Ordner nicht gefunden: {archive_dir}"
                    
                zip_files = [os.path.join(archive_dir, f) for f in os.listdir(archive_dir) if f.lower().endswith('.zip')]
                if not zip_files:
                    return False, f"Keine ZIP-Datei in {archive_dir} gefunden."
                    
                newest_zip = max(zip_files, key=os.path.getmtime)
                shutil.copy2(newest_zip, target_file)
                
                with open(txt_target_file, 'w', encoding='utf-8') as txtf:
                    txtf.write(f"Backup-Protokoll für: {program_name}\n")
                    txtf.write(f"Zeitpunkt: {timestamp}\n")
                    txtf.write(f"Backup-Typ: {backup_type} (OSI Internal Copy)\n")
                    txtf.write("="*50 + "\n\n")
                    txtf.write(f"Kopiert von Original-Datei: {os.path.basename(newest_zip)}\n")
                    txtf.write("Dieses Backup ist eine exakte Kopie des internen OSI-Archivs, um 100% Kompatibilität beim Wiederherstellen zu garantieren.\n")
                    
                logging.info(f"OSI Backup erfolgreich kopiert: {target_file}")
                return True, target_file

            with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(source_path):
                    arcname = os.path.basename(source_path)
                    zipf.write(source_path, arcname)
                    backed_up_files.append(arcname)
                else:
                    if is_selective:
                        # Nur spezifische Dateien sichern (unterstützt Wildcards wie *.MCH)
                        import glob
                        for f_pattern in rule.get("files", []):
                            pattern_path = os.path.join(source_path, f_pattern)
                            for f_path in glob.glob(pattern_path):
                                if os.path.isfile(f_path):
                                    f_name = os.path.relpath(f_path, source_path)
                                    zipf.write(f_path, f_name)
                                    backed_up_files.append(f_name)
                        
                        # Nur spezifische Ordner sichern
                        for folder_name in rule.get("folders", []):
                            # Ensure cross-platform path compatibility
                            folder_rel = folder_name.replace("/", os.sep).replace("\\", os.sep)
                            folder_path = os.path.join(source_path, folder_rel)
                            
                            if os.path.isdir(folder_path):
                                folder_base_name = os.path.basename(folder_path)
                                for root, dirs, files in os.walk(folder_path):
                                    if self.target_base_path in os.path.abspath(root):
                                        continue
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        rel_path = os.path.relpath(file_path, folder_path)
                                        arcname = os.path.join(folder_base_name, rel_path)
                                        if arcname not in backed_up_files:
                                            zipf.write(file_path, arcname)
                                            backed_up_files.append(arcname)
                                            
                        # Zusätzliche absolute Ordner sichern (z.B. OptiPlanning_DATEN)
                        for abs_folder in rule.get("absolute_folders", []):
                            abs_folder_path = os.path.normpath(abs_folder)
                            if os.path.isdir(abs_folder_path):
                                folder_base_name = os.path.basename(abs_folder_path)
                                for root, dirs, files in os.walk(abs_folder_path):
                                    if self.target_base_path in os.path.abspath(root):
                                        continue
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        rel_path = os.path.relpath(file_path, abs_folder_path)
                                        arcname = os.path.join(folder_base_name, rel_path)
                                        if arcname not in backed_up_files:
                                            zipf.write(file_path, arcname)
                                            backed_up_files.append(arcname)

                        # Zusätzliche Ordner aus der Windows Registry auslesen (z.B. Optiplanning)
                        for reg_info in rule.get("registry_paths", []):
                            hive_name = reg_info.get("hive", "HKEY_CURRENT_USER")
                            hive = winreg.HKEY_CURRENT_USER if hive_name == "HKEY_CURRENT_USER" else winreg.HKEY_LOCAL_MACHINE
                            key_path = reg_info.get("key", "")
                            try:
                                with winreg.OpenKey(hive, key_path) as key:
                                    for val_name in reg_info.get("values", []):
                                        try:
                                            val_data, val_type = winreg.QueryValueEx(key, val_name)
                                            if val_data and isinstance(val_data, str):
                                                abs_folder_path = os.path.normpath(val_data)
                                                if os.path.isdir(abs_folder_path):
                                                    for root, dirs, files in os.walk(abs_folder_path):
                                                        if self.target_base_path in os.path.abspath(root):
                                                            continue
                                                        for file in files:
                                                            file_path = os.path.join(root, file)
                                                            rel_path = os.path.relpath(file_path, abs_folder_path)
                                                            # Store under RegistryData_[ValueName] to prevent overwrites
                                                            arcname = os.path.join(f"RegistryData_{val_name}", rel_path)
                                                            if arcname not in backed_up_files:
                                                                zipf.write(file_path, arcname)
                                                                backed_up_files.append(arcname)
                                        except FileNotFoundError:
                                            continue
                            except FileNotFoundError:
                                logging.warning(f"Registry-Schlüssel nicht gefunden: {key_path}")
                    else:
                        # Full Backup (Fallback)
                        for root, dirs, files in os.walk(source_path):
                            # Avoid backing up the backup folder itself if it's inside source
                            if self.target_base_path in os.path.abspath(root):
                                continue
    
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, source_path)
                                zipf.write(file_path, arcname)
                                backed_up_files.append(arcname)

            with open(txt_target_file, 'w', encoding='utf-8') as txtf:
                txtf.write(f"Backup-Protokoll für: {program_name}\n")
                txtf.write(f"Zeitpunkt: {timestamp}\n")
                txtf.write(f"Backup-Typ: {backup_type}\n")
                txtf.write(f"Anzahl gesicherter Dateien: {len(backed_up_files)}\n")
                txtf.write("="*50 + "\n\n")
                txtf.write("Gesicherte Dateien:\n")
                for item in backed_up_files:
                    txtf.write(f"- {item}\n")

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
                    # Also try to remove the corresponding .txt log file
                    txt_path = path.replace('.zip', '.txt')
                    if os.path.exists(txt_path):
                        os.remove(txt_path)
                        logging.info(f"Alte Backup-Logdatei gelöscht: {txt_path}")
                except Exception as e:
                    logging.error(f"Fehler beim Löschen von {path}: {e}")

if __name__ == "__main__":
    # Test block
    logging.basicConfig(level=logging.INFO)
    # ... test logic ...
