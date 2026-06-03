import os

# Definition der Backup-Regeln pro Programm.
# 'type': 'selective' bedeutet, es werden nur die gelisteten Ordner und Dateien gesichert.
# Ist ein Programm nicht gelistet, greift automatisch der Fallback auf ein komplettes Backup ('type': 'full').

BACKUP_RULES = {
    "LPrint": {
        "type": "selective",
        "folders": [
            "Confpd",
            "Dati",
            "LingueU",
            "xml"
        ],
        "files": []
    },
    "LEdit": {
        "type": "selective",
        "folders": [
            "MixedData/Label",
            "MixedData/StdGrafic",
            "Language"
        ],
        "files": [
            "LEditor.ini",
            "Master.ini",
            "Path.dat"
        ]
    },
    "OSI": {
        "type": "copy_latest_zip",
        "folder": "ARCHIVE"
    },
    "Bopti": {
        "type": "selective",
        "folders": [
            "Settings",
            "DatabaseFiles",
            "SqlQueries"
        ],
        "files": [
            "DataBase.sdf"
        ]
    },
    "Optiplanning": {
        "type": "selective",
        "folders": [
            "Cfg",
            "StkCfg",
            "stat",
            "Ddm"
        ],
        "registry_paths": [
            {
                "hive": "HKEY_CURRENT_USER",
                "key": r"Software\Selco S.p.A.\OptiPlanning\1.0",
                "values": [
                    "CpoDir", "JobDir", "LisDir", "MatDir", "OpfDir", "SawDir", 
                    "TgtDir", "TgtDir2", "TgtDir3", "SrcDir", "CabDir", 
                    "BackupDir", "XmlDir", "XmlMatDir", "OsiParDir", "ImgDir", "DbOsiDir"
                ]
            }
        ]
    }
}

def get_backup_rule(program_name):
    """
    Returns the backup rule for the given program name.
    If no specific rule exists, returns a 'full' backup rule.
    """
    # Exakte Übereinstimmung prüfen
    if program_name in BACKUP_RULES:
        return BACKUP_RULES[program_name]
        
    # Teil-Übereinstimmung (z.B. für "Optiplanning_5.1")
    for key, rule in BACKUP_RULES.items():
        if key.lower() in program_name.lower():
            return rule
            
    # Fallback: Alles sichern
    return {"type": "full", "folders": [], "files": []}
