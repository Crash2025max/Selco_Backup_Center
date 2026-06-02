import os
import subprocess
import logging
import datetime

def backup_bopti(manager, source_path, program_name, is_auto):
    """Executes Bopti's internal backup tool if available."""
    # Placeholder for the actual Bopti backup exe path
    bopti_backup_exe = os.path.join(source_path, "BoptiBackup.exe")

    if os.path.exists(bopti_backup_exe):
        try:
            # Assuming it takes arguments or just runs
            subprocess.run([bopti_backup_exe], check=True)
            # After internal backup, we might still want to zip the result to our target path
            # For now, we simulate success
            return True, "Bopti internes Backup ausgeführt"
        except Exception as e:
            return False, f"Bopti Backup Fehler: {e}"
    else:
        # Fallback to standard zip if tool not found
        return manager.create_backup(source_path, program_name, is_auto)

def backup_osi(manager, source_path, program_name, is_auto):
    """Special handling for OSI (e.g. reading DB path from config)."""
    # In a real scenario, we would parse OSI's .ini files here
    # For now, we use the standard zip but it's prepared for specialization
    return manager.create_backup(source_path, program_name, is_auto)
