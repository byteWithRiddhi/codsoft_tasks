"""
Connecta - Contact Manager
==========================
A modern, attractive, professional desktop contact management application
built with Python and CustomTkinter.

Designed for productivity with card-based layouts, real-time search,
favorites, category grouping, stats dashboard, and seamless JSON persistence.
"""

import sys
import os

# Ensure local packages can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from ui.app import ConnectaApp
    except ImportError as e:
        print(f"[Error] Missing dependency: {e}")
        print("Please install requirements using:")
        print("    pip install -r requirements.txt")
        sys.exit(1)

    app = ConnectaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
