import os

def setup_mock_env():
    base = "C:\\BIESSE"
    # Note: On non-Windows this will create a folder named "C:\BIESSE" in the current directory
    # which is fine for testing. On Windows it would try to access C: drive.

    programs = ["Osi", "OptiPlanning", "Bopti", "LEdit", "LPrint"]

    print(f"Erstelle Test-Umgebung in {os.path.abspath(base)}...")

    for p in programs:
        path = os.path.join(base, p)
        if not os.path.exists(path):
            os.makedirs(path)
            # Create a mock exe
            with open(os.path.join(path, f"{p}.exe"), "w") as f:
                f.write("mock")
            print(f" - {p} erstellt.")
        else:
            print(f" - {p} existiert bereits.")

    # Special file for OSI
    with open(os.path.join(base, "Osi", "dbLav.mdb"), "w") as f:
        f.write("mock database")

    print("\nTest-Umgebung bereit! Du kannst nun 'python main.py' starten.")

if __name__ == "__main__":
    setup_mock_env()
