import os
import sys

# Add the project root to sys.path to allow running from any location
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.gui.main_window import App

if __name__ == "__main__":
    app = App()
    app.mainloop()
