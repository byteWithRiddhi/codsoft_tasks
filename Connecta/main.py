import sys
import os

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
