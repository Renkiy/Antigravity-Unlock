import os
import sys

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.gui_app import AntigravityUnlockerApp

if __name__ == "__main__":
    app = AntigravityUnlockerApp()
    app.mainloop()
