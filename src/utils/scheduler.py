import subprocess
import os
import sys
import logging

class Scheduler:
    """Handles Windows Task Scheduler integration via schtasks command."""

    def __init__(self, task_name="HandlBiesseBackup"):
        self.task_name = task_name
        self.python_exe = sys.executable
        # Path to a CLI entry point for the backup
        self.script_path = os.path.abspath("cli_backup.py")

    def create_daily_task(self, start_time="20:00"):
        """Creates a daily backup task."""
        # /SC daily: schedule daily
        # /ST: start time
        # /TR: task run command
        # /F: force create (overwrite)

        command = [
            "schtasks", "/create", "/sc", "daily",
            "/tn", self.task_name,
            "/tr", f'"{self.python_exe}" "{self.script_path}" --auto',
            "/st", start_time,
            "/f"
        ]

        try:
            # We use shell=True only on Windows if needed, but list is safer
            # This will fail on Linux/Mac, which is expected during dev
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"Task {self.task_name} erfolgreich erstellt.")
                return True, "Erfolgreich erstellt."
            else:
                return False, result.stderr
        except Exception as e:
            logging.error(f"Fehler beim Erstellen des Tasks: {e}")
            return False, str(e)

    def delete_task(self):
        command = ["schtasks", "/delete", "/tn", self.task_name, "/f"]
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

if __name__ == "__main__":
    s = Scheduler()
    # print(s.create_daily_task())
