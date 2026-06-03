import os
import platform
import logging

# Try to import win32api for version info, but keep it optional for development on non-Windows
try:
    import win32api
except ImportError:
    win32api = None

class BiesseScanner:
    def __init__(self, base_path="C:\\BIESSE"):
        # Support for environment variable to override base path during development/testing
        self.base_path = os.getenv("BIESSE_BASE_PATH", base_path)
        self.programs = {
            "OSI": {"folder": "Osi", "exe": "Osi.exe"},
            "Optiplanning": {"folder": "OptiPlanning", "exe": "OptiPlanning.exe"},
            "Bopti": {"folder": "Bopti", "exe": "Bopti.exe"},
            "LEdit": {"folder": "LEdit", "exe": "LEdit.exe"},
            "LPrint": {"folder": "LPrint", "exe": "LPrint.exe"}
        }

    def scan(self):
        """Scans the base path for Biesse programs."""
        import glob
        results = {}
        if not os.path.exists(self.base_path):
            logging.warning(f"Basisverzeichnis {self.base_path} nicht gefunden.")
            # Return empty or marked as not installed
            for name in self.programs:
                results[name] = {"installed": False}
            return results

        for name, info in self.programs.items():
            if name == "OSI":
                prog_path = os.path.join(self.base_path, info["folder"])
                if os.path.exists(prog_path):
                    version = self._get_version(prog_path, info["exe"])
                    event_log_path = os.path.join(prog_path, "EVENTS", "Event.log")
                    if os.path.exists(event_log_path):
                        try:
                            with open(event_log_path, 'r', encoding='latin-1', errors='ignore') as f:
                                lines = f.readlines()
                                for line in reversed(lines):
                                    if "Version \t\tUI:" in line or "Version \tUI:" in line or "UI: " in line:
                                        if "UI: " in line and "-" in line:
                                            version = line.split("UI:")[1].split("-")[0].strip()
                                            break
                        except Exception as e:
                            logging.error(f"Fehler beim Lesen der OSI-Version: {e}")
                            
                    results[name] = {
                        "installed": True,
                        "path": prog_path,
                        "version": version
                    }
                else:
                    results[name] = {"installed": False}
                continue

            if name == "Optiplanning":
                pattern = os.path.join(self.base_path, "OptiPlanning*")
                matches = glob.glob(pattern)
                valid_matches = [m for m in matches if os.path.isdir(m) and not m.endswith("_DATEN")]
                
                if valid_matches:
                    for prog_path in valid_matches:
                        exe_path = os.path.join(prog_path, "System", "OptiPlan.exe")
                        if not os.path.exists(exe_path):
                            exe_path = os.path.join(prog_path, info["exe"])
                            
                        version = "Nicht gefunden"
                        if os.path.exists(exe_path):
                            version = self._get_version(os.path.dirname(exe_path), os.path.basename(exe_path))
                            
                        if version == "0.0.0.0" or version == "Nicht gefunden":
                            folder_name = os.path.basename(prog_path)
                            if "_V" in folder_name:
                                version = folder_name.split("_V")[-1]
                                
                        unique_key = f"Optiplanning_{version}"
                        results[unique_key] = {
                            "name": "Optiplanning",
                            "installed": True,
                            "path": prog_path,
                            "version": version
                        }
                else:
                    results[name] = {"installed": False}
                continue

            # Support both backslash and forward slash for cross-platform dev
            prog_path = os.path.join(self.base_path, info["folder"])
            if os.path.exists(prog_path):
                version = self._get_version(prog_path, info["exe"])
                results[name] = {
                    "installed": True,
                    "path": prog_path,
                    "version": version
                }
            else:
                results[name] = {"installed": False}

        return results

    def _get_version(self, folder, exe_name):
        """Try to extract version info from exe or config files."""
        exe_path = os.path.join(folder, exe_name)
        if not os.path.exists(exe_path):
            return "Nicht gefunden"

        if win32api:
            try:
                # Try reading StringFileInfo first (handles cases where FixedFileInfo is 0.0.0.0)
                lang, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
                str_info = '\\StringFileInfo\\%04X%04X\\FileVersion' % (lang, codepage)
                str_version = win32api.GetFileVersionInfo(exe_path, str_info)
                if str_version and str_version.strip() and str_version.strip() != "0.0.0.0":
                    return str_version.strip()
            except Exception:
                pass

            try:
                info = win32api.GetFileVersionInfo(exe_path, "\\")
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                return version
            except Exception as e:
                logging.error(f"Fehler beim Lesen der Version von {exe_name}: {e}")

        return "Version erkannt (Details nur auf Windows)"

    @staticmethod
    def get_pc_name():
        return platform.node()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = BiesseScanner()
    print(f"PC Name: {scanner.get_pc_name()}")
    print("Gefundene Programme:")
    print(scanner.scan())
