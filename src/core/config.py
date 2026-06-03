import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.defaults = {
            "auto_backup": {
                "path": "C:\\Backups\\Auto",
                "programs": {
                    "OSI": {"enabled": True},
                    "Optiplanning": {"enabled": True},
                    "Bopti": {"enabled": True},
                    "LEdit": {"enabled": True},
                    "LPrint": {"enabled": True}
                },
                "schedule": {
                    "type": "DAILY",
                    "time": "12:15",
                    "minute_interval": 15
                }
            },
            "manual_backup": {
                "path": "C:\\Backups\\Manuell",
                "programs": {
                    "OSI": {"enabled": True},
                    "Optiplanning": {"enabled": True},
                    "Bopti": {"enabled": True},
                    "LEdit": {"enabled": True},
                    "LPrint": {"enabled": True}
                }
            },
            "retention": {
                "count": 10
            },
            "window": {
                "geometry": "900x650"
            }
        }
        self.config = self.load_config()

    def load_config(self):
        config = self.defaults.copy()
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    
                    # Migration from v1.1.0 to v1.3.0 format
                    if "backup_paths" in loaded:
                        config["auto_backup"]["path"] = loaded["backup_paths"].get("auto", config["auto_backup"]["path"])
                        config["manual_backup"]["path"] = loaded["backup_paths"].get("manual", config["manual_backup"]["path"])
                    if "programs" in loaded:
                        config["auto_backup"]["programs"] = loaded.get("programs", {})
                        config["manual_backup"]["programs"] = loaded.get("programs", {})
                    if "schedule" in loaded:
                        config["auto_backup"]["schedule"] = loaded.get("schedule", {})
                        
                    # If it's already the new format, just update the loaded keys
                    if "auto_backup" in loaded:
                        config["auto_backup"].update(loaded["auto_backup"])
                    if "manual_backup" in loaded:
                        config["manual_backup"].update(loaded["manual_backup"])
                    if "retention" in loaded:
                        config["retention"].update(loaded["retention"])
                    if "window" in loaded:
                        config["window"].update(loaded["window"])
                        
                    return config
            except Exception as e:
                logging.error(f"Fehler beim Laden der Konfiguration: {e}")
        return config

    def save_config(self, config=None):
        if config:
            self.config = config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        return self.save_config()

if __name__ == "__main__":
    cm = ConfigManager("test_config.json")
    print(cm.config)
    cm.save_config()
