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
        self.extra_paths = ["D:\\BIESSE", "E:\\BIESSE"]
        self.programs = {
            "OSI": {"pattern": "osi", "exe": "Osi.exe"},
            "Optiplanning": {"pattern": "optiplanning", "exe": "OptiPlanning.exe"},
            "Bopti": {"pattern": "bopti", "exe": "Bopti.exe"},
            "LEdit": {"pattern": "ledit", "exe": "LEdit.exe"},
            "LPrint": {"pattern": "lprint", "exe": "LPrint.exe"}
        }

    def scan(self):
        """Scans the base path and extra paths for Biesse programs."""
        results = {}

        # Initialize all as not found
        for name in self.programs:
            results[name] = {"installed": False}

        search_paths = [self.base_path] + self.extra_paths

        for base in search_paths:
            if not os.path.exists(base):
                continue

            try:
                actual_folders = os.listdir(base)
                for folder in actual_folders:
                    folder_lower = folder.lower()
                    folder_full_path = os.path.join(base, folder)

                    if not os.path.isdir(folder_full_path):
                        continue

                    for name, info in self.programs.items():
                        # Only update if not already found (or we could store multiple)
                        if not results[name]["installed"] and info["pattern"] in folder_lower:
                            version = self._get_version(folder_full_path, info["exe"])
                            results[name] = {
                                "installed": True,
                                "path": folder_full_path,
                                "version": version,
                                "folder_name": f"{os.path.basename(base)}\\{folder}"
                            }
            except Exception as e:
                logging.error(f"Fehler beim Scannen von {base}: {e}")

        return results

    def _get_version(self, folder, exe_name):
        """Try to extract version info from exe or config files."""
        # Special check for OSI version files
        version_file = os.path.join(folder, "Version.txt")
        if os.path.exists(version_file):
            try:
                with open(version_file, "r") as f:
                    return f.read().strip()
            except Exception:
                pass

        exe_path = os.path.join(folder, exe_name)
        if not os.path.exists(exe_path):
            return "Nicht gefunden"

        if win32api:
            try:
                info = win32api.GetFileVersionInfo(exe_path, "\\")
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                return version
            except Exception as e:
                logging.debug(f"Fehler beim Lesen der EXE Version von {exe_name}: {e}")

        # Fallback: check any .ini or .xml for version strings
        for f in os.listdir(folder):
            if f.lower().endswith(".ini"):
                try:
                    with open(os.path.join(folder, f), "r", errors="ignore") as file:
                        content = file.read()
                        if "Version=" in content:
                            return content.split("Version=")[1].split("\n")[0].strip()
                except Exception:
                    continue

        return "Erkannt"

    @staticmethod
    def get_pc_name():
        return platform.node()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scanner = BiesseScanner()
    print(f"PC Name: {scanner.get_pc_name()}")
    print("Gefundene Programme:")
    print(scanner.scan())
