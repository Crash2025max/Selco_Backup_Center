import json
import os
import logging

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.defaults = {
            "backup_paths": {
                "auto": "C:\\Backups\\Auto",
                "manual": "C:\\Backups\\Manuell"
            },
            "retention": {
                "count": 10
            },
            "programs": {
                "OSI": {"enabled": True},
                "Optiplanning": {"enabled": True},
                "Bopti": {"enabled": True},
                "LEdit": {"enabled": True},
                "LPrint": {"enabled": True}
            },
            "schedule": {
                "interval_days": 1,
                "time": "20:00"
            }
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Fehler beim Laden der Konfiguration: {e}")
        return self.defaults.copy()

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
