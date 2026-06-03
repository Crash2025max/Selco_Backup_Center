import os
import sys
import threading
import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.core.config import ConfigManager
from src.core.scanner import BiesseScanner
from src.core.backup import BackupManager
from src.core.scheduler import TaskScheduler

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_version = "1.2.0"
        self.title(f"Handl Biesse Backup Manager (v{self.app_version})")
        
        self.config_manager = ConfigManager()
        self.scanner = BiesseScanner()
        self.scheduler = TaskScheduler()

        # Load window geometry
        geom = self.config_manager.get("window", {}).get("geometry", "900x650")
        self.geometry(geom)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # UI Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Biesse Backup", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_auto = ctk.CTkButton(self.sidebar_frame, text="Auto Backup (Kunden)", command=self.show_auto_frame)
        self.btn_auto.grid(row=1, column=0, padx=20, pady=10)

        self.btn_manual = ctk.CTkButton(self.sidebar_frame, text="Manuelles Backup (Service)", command=self.show_manual_frame)
        self.btn_manual.grid(row=2, column=0, padx=20, pady=10)

        self.btn_scan = ctk.CTkButton(self.sidebar_frame, text="System manuell scannen", command=self.run_scan_thread)
        self.btn_scan.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{self.app_version}", text_color="gray", font=ctk.CTkFont(size=11))
        self.version_label.grid(row=5, column=0, padx=20, pady=20, sticky="s")

        # Main Container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Variables for Checkboxes
        self.auto_program_vars = {}
        self.manual_program_vars = {}
        self.auto_time_labels = {}
        self.manual_time_labels = {}
        self.scan_results = {}
        self.auto_frame = ctk.CTkScrollableFrame(self.main_container)
        self.manual_frame = ctk.CTkScrollableFrame(self.main_container)
        
        self.setup_auto_frame()
        self.setup_manual_frame()

        # Log Textbox (Shared at the bottom of column 1)
        self.log_textbox = ctk.CTkTextbox(self, height=120)
        self.log_textbox.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="nsew")
        self.log_textbox.configure(state="disabled")

        # Initial View
        self.show_auto_frame()
        self.run_scan_thread()

    def show_auto_frame(self):
        self.manual_frame.grid_forget()
        self.auto_frame.grid(row=0, column=0, sticky="nsew")
        self.btn_auto.configure(fg_color=("gray75", "gray25"))
        self.btn_manual.configure(fg_color=["#3a7ebf", "#1f538d"])

    def show_manual_frame(self):
        self.auto_frame.grid_forget()
        self.manual_frame.grid(row=0, column=0, sticky="nsew")
        self.btn_manual.configure(fg_color=("gray75", "gray25"))
        self.btn_auto.configure(fg_color=["#3a7ebf", "#1f538d"])

    def setup_auto_frame(self):
        title = ctk.CTkLabel(self.auto_frame, text="Automatische Backups (Kunden-Setup)", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 20), anchor="w")

        # Path
        ctk.CTkLabel(self.auto_frame, text="Speicherort für Auto-Backups:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w")
        path_frame = ctk.CTkFrame(self.auto_frame)
        path_frame.pack(fill="x", pady=5)
        self.auto_path_entry = ctk.CTkEntry(path_frame)
        self.auto_path_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.auto_path_entry.insert(0, self.config_manager.get("auto_backup", {}).get("path", "C:\\Backups\\Auto"))
        ctk.CTkButton(path_frame, text="...", width=30, command=lambda: self.browse_path("auto")).pack(side="left", padx=5)

        # Retention
        ctk.CTkLabel(self.auto_frame, text="Anzahl behaltener Backups:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), anchor="w")
        self.retention_entry = ctk.CTkEntry(self.auto_frame)
        self.retention_entry.pack(pady=5, anchor="w")
        self.retention_entry.insert(0, str(self.config_manager.get("retention", {}).get("count", 10)))

        # Programs
        ctk.CTkLabel(self.auto_frame, text="Programme für Automatisches Backup:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), anchor="w")
        self.auto_checkbox_frame = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        self.auto_checkbox_frame.pack(fill="x")

        # Schedule
        ctk.CTkLabel(self.auto_frame, text="Zeitplan (Windows Aufgabenplanung):", font=ctk.CTkFont(weight="bold")).pack(pady=(30, 5), anchor="w")
        
        sched_config = self.config_manager.get("auto_backup", {}).get("schedule", {})
        self.schedule_mode_var = ctk.StringVar(value=sched_config.get("type", "DAILY"))
        
        mode_frame = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        mode_frame.pack(fill="x", pady=5)
        ctk.CTkRadioButton(mode_frame, text="Täglich", variable=self.schedule_mode_var, value="DAILY", command=self.update_schedule_inputs).pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(mode_frame, text="Minütlich (Test)", variable=self.schedule_mode_var, value="MINUTE", command=self.update_schedule_inputs).pack(side="left", padx=10)
        
        self.inputs_frame = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        self.inputs_frame.pack(fill="x", pady=10)

        self.daily_frame = ctk.CTkFrame(self.inputs_frame, fg_color="transparent")
        ctk.CTkLabel(self.daily_frame, text="Uhrzeit (HH:MM):", width=100, anchor="w").pack(side="left")
        self.time_entry = ctk.CTkEntry(self.daily_frame, width=100)
        self.time_entry.pack(side="left", padx=10)
        self.time_entry.insert(0, sched_config.get("time", "12:15"))
        
        self.minute_frame = ctk.CTkFrame(self.inputs_frame, fg_color="transparent")
        ctk.CTkLabel(self.minute_frame, text="Alle X Minuten:", width=100, anchor="w").pack(side="left")
        self.minute_entry = ctk.CTkEntry(self.minute_frame, width=100)
        self.minute_entry.pack(side="left", padx=10)
        self.minute_entry.insert(0, str(sched_config.get("minute_interval", 15)))
        
        self.update_schedule_inputs()
        
        # Schedule Buttons
        btn_frame = ctk.CTkFrame(self.auto_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        ctk.CTkButton(btn_frame, text="Zeitplan anlegen/ändern", command=self.apply_schedule).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Zeitplan löschen", fg_color="darkred", hover_color="red", command=self.delete_schedule).pack(side="left")
        
        self.schedule_status_label = ctk.CTkLabel(self.auto_frame, text="", text_color="gray", font=ctk.CTkFont(size=14, weight="bold"))
        self.schedule_status_label.pack(pady=5, anchor="w")
        self.refresh_schedule_status()

    def setup_manual_frame(self):
        title = ctk.CTkLabel(self.manual_frame, text="Manuelles Backup (Service/Techniker)", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 20), anchor="w")

        # Path
        ctk.CTkLabel(self.manual_frame, text="Speicherort für Manuelles Backup:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5), anchor="w")
        path_frame = ctk.CTkFrame(self.manual_frame)
        path_frame.pack(fill="x", pady=5)
        self.manual_path_entry = ctk.CTkEntry(path_frame)
        self.manual_path_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.manual_path_entry.insert(0, self.config_manager.get("manual_backup", {}).get("path", "C:\\Backups\\Manuell"))
        ctk.CTkButton(path_frame, text="...", width=30, command=lambda: self.browse_path("manual")).pack(side="left", padx=5)

        # Programs
        ctk.CTkLabel(self.manual_frame, text="Programme JETZT sichern:", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5), anchor="w")
        self.manual_checkbox_frame = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        self.manual_checkbox_frame.pack(fill="x")

        # Start Button
        ctk.CTkButton(self.manual_frame, text="▶ Backup Jetzt Starten", font=ctk.CTkFont(weight="bold"), 
                      height=40, command=self.run_manual_backup_thread).pack(pady=40, anchor="w")

    def update_schedule_inputs(self):
        mode = self.schedule_mode_var.get()
        if mode == "DAILY":
            self.minute_frame.pack_forget()
            self.daily_frame.pack(fill="x", pady=5)
        else:
            self.daily_frame.pack_forget()
            self.minute_frame.pack(fill="x", pady=5)

    def browse_path(self, type_):
        path = filedialog.askdirectory()
        if path:
            if type_ == "auto":
                self.auto_path_entry.delete(0, "end")
                self.auto_path_entry.insert(0, path)
            elif type_ == "manual":
                self.manual_path_entry.delete(0, "end")
                self.manual_path_entry.insert(0, path)

    def log(self, message, level="INFO"):
        prefix = f"[{level}] " if level != "INFO" else ""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{prefix}{message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def run_scan_thread(self):
        self.log("Starte System-Scan im Hintergrund...")
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.scan_results = self.scanner.scan()
        # Schedule UI update on main thread
        self.after(0, self.update_checkboxes_ui)

    def update_checkboxes_ui(self):
        # Clear existing
        for widget in self.auto_checkbox_frame.winfo_children():
            widget.destroy()
        for widget in self.manual_checkbox_frame.winfo_children():
            widget.destroy()
            
        self.auto_checkbox_frame.grid_columnconfigure(0, weight=0)
        self.auto_checkbox_frame.grid_columnconfigure(1, weight=0)
        self.manual_checkbox_frame.grid_columnconfigure(0, weight=0)
        self.manual_checkbox_frame.grid_columnconfigure(1, weight=0)
            
        self.auto_program_vars.clear()
        self.manual_program_vars.clear()
        self.auto_time_labels.clear()
        self.manual_time_labels.clear()
        
        auto_progs = self.config_manager.get("auto_backup", {}).get("programs", {})
        manual_progs = self.config_manager.get("manual_backup", {}).get("programs", {})
        
        row_idx = 0
        for prog_name, info in self.scan_results.items():
            if info["installed"]:
                display_name = info.get("name", prog_name)
                
                # Auto Checkbox
                var_auto = ctk.BooleanVar(value=auto_progs.get(prog_name, {}).get("enabled", True))
                cb_auto = ctk.CTkCheckBox(self.auto_checkbox_frame, text=display_name, variable=var_auto)
                cb_auto.grid(row=row_idx, column=0, pady=4, sticky="w")
                
                v_lbl_auto = ctk.CTkLabel(self.auto_checkbox_frame, text=f"  v{info['version']}  ", text_color="gray", font=ctk.CTkFont(size=12), fg_color=("gray85", "gray20"), corner_radius=4)
                v_lbl_auto.grid(row=row_idx, column=1, padx=(10, 0), pady=4, sticky="w")
                
                t_lbl_auto = ctk.CTkLabel(self.auto_checkbox_frame, text="-", text_color="gray", font=ctk.CTkFont(size=11))
                t_lbl_auto.grid(row=row_idx, column=2, padx=(10, 0), pady=4, sticky="w")
                
                self.auto_program_vars[prog_name] = var_auto
                self.auto_time_labels[prog_name] = t_lbl_auto
                
                # Manual Checkbox
                var_manual = ctk.BooleanVar(value=manual_progs.get(prog_name, {}).get("enabled", True))
                cb_manual = ctk.CTkCheckBox(self.manual_checkbox_frame, text=display_name, variable=var_manual)
                cb_manual.grid(row=row_idx, column=0, pady=4, sticky="w")
                
                v_lbl_manual = ctk.CTkLabel(self.manual_checkbox_frame, text=f"  v{info['version']}  ", text_color="gray", font=ctk.CTkFont(size=12), fg_color=("gray85", "gray20"), corner_radius=4)
                v_lbl_manual.grid(row=row_idx, column=1, padx=(10, 0), pady=4, sticky="w")
                
                t_lbl_manual = ctk.CTkLabel(self.manual_checkbox_frame, text="-", text_color="gray", font=ctk.CTkFont(size=11))
                t_lbl_manual.grid(row=row_idx, column=2, padx=(10, 0), pady=4, sticky="w")
                
                self.manual_program_vars[prog_name] = var_manual
                self.manual_time_labels[prog_name] = t_lbl_manual
                row_idx += 1
                
                self.log(f"Gefunden: {display_name} (v{info['version']})")
                
        self.refresh_last_backup_times()

    def refresh_last_backup_times(self):
        auto_path = self.config_manager.get("auto_backup", {}).get("path", "")
        manual_path = self.config_manager.get("manual_backup", {}).get("path", "")
        
        def get_time_for_prog(path, is_auto, prog_name):
            if not path or not os.path.exists(path):
                return "Nie"
            tag = "_Auto_" if is_auto else "_Manuell_"
            latest = 0
            try:
                for f in os.listdir(path):
                    if tag in f and prog_name in f and f.endswith(".zip"):
                        mtime = os.path.getmtime(os.path.join(path, f))
                        if mtime > latest:
                            latest = mtime
            except Exception:
                pass
            if latest == 0:
                return "Nie"
            return datetime.datetime.fromtimestamp(latest).strftime("Zuletzt: %d.%m.%y %H:%M")
            
        for prog, lbl in self.auto_time_labels.items():
            lbl.configure(text=get_time_for_prog(auto_path, True, prog))
            
        for prog, lbl in self.manual_time_labels.items():
            lbl.configure(text=get_time_for_prog(manual_path, False, prog))

    def refresh_schedule_status(self):
        is_active = self.scheduler.is_task_active()
        if is_active:
            self.schedule_status_label.configure(text="Status: Zeitplan ist AKTIV", text_color="green")
        else:
            self.schedule_status_label.configure(text="Status: Kein Zeitplan aktiv", text_color="gray")

    def apply_schedule(self):
        self.save_current_config() # Save path and programs first
        
        mode = self.schedule_mode_var.get()
        time_str = self.time_entry.get()
        try:
            minutes = int(self.minute_entry.get())
        except ValueError:
            minutes = 15
            
        success, msg = self.scheduler.create_or_update_task(mode, time_str, minutes)
        if success:
            sched_config = self.config_manager.get("auto_backup", {}).get("schedule", {})
            sched_config["type"] = mode
            sched_config["time"] = time_str
            sched_config["minute_interval"] = minutes
            
            auto_conf = self.config_manager.get("auto_backup", {})
            auto_conf["schedule"] = sched_config
            self.config_manager.set("auto_backup", auto_conf)
            
            self.log(msg)
            messagebox.showinfo("Erfolg", msg)
        else:
            self.log(f"Fehler: {msg}", level="ERROR")
            messagebox.showerror("Fehler", msg)
            
        self.refresh_schedule_status()

    def delete_schedule(self):
        success, msg = self.scheduler.delete_task()
        if success:
            self.log(msg)
            messagebox.showinfo("Gelöscht", msg)
        else:
            self.log(f"Fehler: {msg}", level="ERROR")
            messagebox.showerror("Fehler", msg)
        self.refresh_schedule_status()

    def run_manual_backup_thread(self):
        self.save_current_config()
        
        # Check if OSI is selected for manual backup
        osi_var = self.manual_program_vars.get("OSI")
        if osi_var and osi_var.get() and self.scan_results.get("OSI", {}).get("installed"):
            response = messagebox.askyesno(
                "Wichtiger Hinweis zu OSI",
                "Da OSI für das Backup ein internes Archiv nutzt, muss dieses vor dem Sichern auf dem aktuellsten Stand sein.\n\n"
                "Hast du in der OSI-Maschinenoberfläche bereits manuell ein aktuelles Backup erstellt und ist dieses fertiggestellt?",
                icon="warning"
            )
            if not response:
                self.log("Manuelles Backup abgebrochen, da das OSI-Archiv noch nicht aktualisiert wurde.", level="INFO")
                return

        threading.Thread(target=self.run_manual_backup, daemon=True).start()

    def run_manual_backup(self):
        manual_path = self.manual_path_entry.get()
        manager = BackupManager(manual_path)

        self.log("Starte MANUELLES Backup...")
        for name, var in self.manual_program_vars.items():
            if var.get() and self.scan_results.get(name, {}).get("installed"):
                self.log(f"Sichere {name}...")
                success, msg = manager.create_backup(self.scan_results[name]["path"], name, is_auto=False)
                if success:
                    if manager.verify_backup(msg):
                        self.log(f"Erfolgreich & Verifiziert: {os.path.basename(msg)}")
                    else:
                        self.log(f"FEHLER: Zip-Integritätsprüfung für {os.path.basename(msg)} fehlgeschlagen!", level="ERROR")
                else:
                    self.log(f"FEHLER bei {name}: {msg}", level="ERROR")
        
        self.log("Manuelles Backup abgeschlossen!")
        # Use after to show messagebox from main thread
        self.after(0, self.refresh_last_backup_times)
        self.after(0, lambda: messagebox.showinfo("Backup", "Manuelles Backup abgeschlossen!"))

    def save_current_config(self):
        """Saves current UI state to config without closing the app."""
        # Save Auto Settings
        auto_config = self.config_manager.get("auto_backup", {})
        auto_config["path"] = self.auto_path_entry.get()
        
        auto_progs = {}
        for prog, var in self.auto_program_vars.items():
            auto_progs[prog] = {"enabled": var.get()}
        auto_config["programs"] = auto_progs
        self.config_manager.set("auto_backup", auto_config)
        
        # Save Manual Settings
        manual_config = self.config_manager.get("manual_backup", {})
        manual_config["path"] = self.manual_path_entry.get()
        
        manual_progs = {}
        for prog, var in self.manual_program_vars.items():
            manual_progs[prog] = {"enabled": var.get()}
        manual_config["programs"] = manual_progs
        self.config_manager.set("manual_backup", manual_config)
        
        # Save Retention
        try:
            count = int(self.retention_entry.get())
        except ValueError:
            count = 10
        self.config_manager.set("retention", {"count": count})

    def on_closing(self):
        """Called when the user clicks the X to close the window."""
        self.save_current_config()
        
        # Save Window Geometry
        self.config_manager.set("window", {"geometry": self.geometry()})
        
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
