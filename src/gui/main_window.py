import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from src.core.scanner import BiesseScanner
from src.core.config import ConfigManager
from src.core.backup import BackupManager

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Handl Biesse Backup Manager")
        self.geometry("800x600")

        self.config_manager = ConfigManager()
        self.scanner = BiesseScanner()
        self.backup_manager = None # Will be initialized based on paths

        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Biesse Backup", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.scan_button = ctk.CTkButton(self.sidebar_frame, text="Software Scan", command=self.run_scan)
        self.scan_button.grid(row=1, column=0, padx=20, pady=10)

        self.manual_backup_button = ctk.CTkButton(self.sidebar_frame, text="Manuelles Backup", command=self.run_manual_backup)
        self.manual_backup_button.grid(row=2, column=0, padx=20, pady=10)

        # Main Content
        self.main_frame = ctk.CTkScrollableFrame(self, label_text="Einstellungen & Status")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Paths
        self.path_label = ctk.CTkLabel(self.main_frame, text="Backup Pfade", font=ctk.CTkFont(weight="bold"))
        self.path_label.pack(pady=(10, 5), anchor="w")

        self.auto_path_frame = ctk.CTkFrame(self.main_frame)
        self.auto_path_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(self.auto_path_frame, text="Auto-Pfad: ", width=100).pack(side="left", padx=5)
        self.auto_path_entry = ctk.CTkEntry(self.auto_path_frame)
        self.auto_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.auto_path_entry.insert(0, self.config_manager.get("backup_paths")["auto"])
        ctk.CTkButton(self.auto_path_frame, text="...", width=30, command=lambda: self.browse_path("auto")).pack(side="left", padx=5)

        self.manual_path_frame = ctk.CTkFrame(self.main_frame)
        self.manual_path_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(self.manual_path_frame, text="Manuell-Pfad: ", width=100).pack(side="left", padx=5)
        self.manual_path_entry = ctk.CTkEntry(self.manual_path_frame)
        self.manual_path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.manual_path_entry.insert(0, self.config_manager.get("backup_paths")["manual"])
        ctk.CTkButton(self.manual_path_frame, text="...", width=30, command=lambda: self.browse_path("manual")).pack(side="left", padx=5)

        self.debug_var = ctk.BooleanVar(value=False)
        self.debug_cb = ctk.CTkCheckBox(self.main_frame, text="Debug-Modus (Ausführliches Logging)", variable=self.debug_var)
        self.debug_cb.pack(pady=10, anchor="w")

        # Programs
        self.prog_label = ctk.CTkLabel(self.main_frame, text="Programme zum Sichern", font=ctk.CTkFont(weight="bold"))
        self.prog_label.pack(pady=(20, 5), anchor="w")

        self.program_vars = {}
        for prog in ["OSI", "Optiplanning", "Bopti", "LEdit", "LPrint"]:
            var = ctk.BooleanVar(value=self.config_manager.get("programs", {}).get(prog, {}).get("enabled", True))
            cb = ctk.CTkCheckBox(self.main_frame, text=prog, variable=var)
            cb.pack(pady=2, anchor="w")
            self.program_vars[prog] = var

        # Retention
        self.retention_label = ctk.CTkLabel(self.main_frame, text="Anzahl behaltener Auto-Backups", font=ctk.CTkFont(weight="bold"))
        self.retention_label.pack(pady=(20, 5), anchor="w")
        self.retention_entry = ctk.CTkEntry(self.main_frame)
        self.retention_entry.pack(pady=5, anchor="w")
        self.retention_entry.insert(0, str(self.config_manager.get("retention")["count"]))

        # Status
        self.status_text = ctk.CTkTextbox(self, height=150)
        self.status_text.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")

    def log(self, message, level="INFO"):
        if level == "DEBUG" and not self.debug_var.get():
            return
        prefix = f"[{level}] " if self.debug_var.get() else ""
        self.status_text.insert("end", f"{prefix}{message}\n")
        self.status_text.see("end")

    def browse_path(self, type_):
        path = filedialog.askdirectory()
        if path:
            if type_ == "auto":
                self.auto_path_entry.delete(0, "end")
                self.auto_path_entry.insert(0, path)
            elif type_ == "manual":
                self.manual_path_entry.delete(0, "end")
                self.manual_path_entry.insert(0, path)

    def run_scan(self):
        self.log("Starte Software-Scan...")
        results = self.scanner.scan()
        for name, info in results.items():
            status = f"Gefunden (v{info['version']})" if info["installed"] else "Nicht installiert"
            self.log(f"{name}: {status}")

    def run_manual_backup(self):
        # Save current config first
        manual_path = self.manual_path_entry.get()

        results = self.scanner.scan()
        manager = BackupManager(manual_path)

        self.log("Starte manuelles Backup...")
        for name, var in self.program_vars.items():
            if var.get() and results.get(name, {}).get("installed"):
                self.log(f"Sichere {name}...")
                success, msg = manager.create_backup(results[name]["path"], name, is_auto=False)
                if success:
                    if manager.verify_backup(msg):
                        self.log(f"Erfolgreich & Verifiziert: {os.path.basename(msg)}")
                    else:
                        self.log(f"Erstellt, aber VERIFIKATION FEHLGESCHLAGEN: {os.path.basename(msg)}")
                else:
                    self.log(f"FEHLER bei {name}: {msg}")

        messagebox.showinfo("Backup", "Manuelles Backup abgeschlossen!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
