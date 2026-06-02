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
        results = {}
        if not os.path.exists(self.base_path):
            logging.warning(f"Basisverzeichnis {self.base_path} nicht gefunden.")
            # Return empty or marked as not installed
            for name in self.programs:
                results[name] = {"installed": False}
            return results

        for name, info in self.programs.items():
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
