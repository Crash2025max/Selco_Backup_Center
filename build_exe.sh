# Build script for Handl Biesse Backup Manager

# Install PyInstaller if not present
# pip install pyinstaller

# Build the main GUI app
# --onefile: single executable
# --noconsole: no terminal window for GUI
# --name: output name
# --add-data: include necessary folders if any

pyinstaller --onefile --noconsole --name "Handl_Biesse_Backup_Manager" main.py

# Build the CLI tool for the scheduler
pyinstaller --onefile --name "cli_backup" cli_backup.py
