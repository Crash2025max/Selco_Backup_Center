import os
import sys
import subprocess
import logging

class TaskScheduler:
    def __init__(self, task_name="Handl_Biesse_AutoBackup"):
        self.task_name = task_name
        
        # Define the path to the cli_backup.py script
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.script_path = os.path.join(project_root, "cli_backup.py")
        
        # Check if running as a compiled exe or python script
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            self.command = f'"{sys.executable}" --auto'
        else:
            # Running as normal python script
            # Use sys.executable to use the same python interpreter (with dependencies)
            self.command = f'"{sys.executable}" "{self.script_path}" --auto'

    def create_or_update_task(self, schedule_type="DAILY", time_str="12:15", minutes=15):
        """
        Creates or updates a Windows scheduled task using schtasks.
        schedule_type: "DAILY" or "MINUTE"
        time_str: "HH:MM" (e.g. 12:15)
        minutes: int (e.g. 15 for 15-minute interval)
        """
        try:
            if schedule_type == "DAILY":
                cmd = [
                    "schtasks", "/Create", 
                    "/TN", self.task_name, 
                    "/TR", self.command, 
                    "/SC", "DAILY", 
                    "/ST", time_str,
                    "/F" # Force overwrite if exists
                ]
            elif schedule_type == "MINUTE":
                cmd = [
                    "schtasks", "/Create", 
                    "/TN", self.task_name, 
                    "/TR", self.command, 
                    "/SC", "MINUTE", 
                    "/MO", str(minutes),
                    "/F"
                ]
            else:
                return False, "Unbekannter Zeitplan-Typ"

            # Execute the command
            # Note: We must encode properly for Windows, or let subprocess handle it.
            # Using creationflags=0x08000000 (CREATE_NO_WINDOW) to prevent console popup
            creationflags = 0
            if sys.platform == "win32":
                creationflags = 0x08000000
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=creationflags)
            logging.info(f"Task erfolgreich erstellt: {result.stdout}")
            return True, "Zeitplan erfolgreich erstellt und in Windows registriert."
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logging.error(f"Fehler beim Erstellen des Tasks: {error_msg}")
            
            # Provide user-friendly messages for common errors like missing admin rights
            if "Zugriff verweigert" in error_msg or "Access is denied" in error_msg:
                return False, "Zugriff verweigert! Bitte starte das Programm als Administrator, um Zeitpläne anzulegen."
                
            return False, error_msg

    def delete_task(self):
        """Deletes the scheduled task from Windows."""
        try:
            cmd = ["schtasks", "/Delete", "/TN", self.task_name, "/F"]
            creationflags = 0
            if sys.platform == "win32":
                creationflags = 0x08000000
                
            subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=creationflags)
            logging.info("Task erfolgreich gelöscht.")
            return True, "Zeitplan erfolgreich gelöscht."
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            if "angegebene Aufgabe wurde nicht gefunden" in error_msg or "cannot find the file" in error_msg.lower():
                return True, "Zeitplan existierte nicht oder war bereits gelöscht."
                
            logging.error(f"Fehler beim Löschen des Tasks: {error_msg}")
            
            if "Zugriff verweigert" in error_msg or "Access is denied" in error_msg:
                return False, "Zugriff verweigert! Bitte starte das Programm als Administrator, um Zeitpläne zu löschen."
                
            return False, error_msg
            
    def is_task_active(self):
        """Checks if the task exists in Windows Task Scheduler."""
        try:
            cmd = ["schtasks", "/Query", "/TN", self.task_name]
            creationflags = 0
            if sys.platform == "win32":
                creationflags = 0x08000000
                
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=creationflags)
            return result.returncode == 0
        except Exception:
            return False
