"""
main.py - Entry point for the Clinical Data Warehouse application.

Usage:
    python main.py

The program launches a Tkinter GUI window.
All data files are expected under the ./Data directory.
"""

import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ui import ClinicalApp


def main():
    root = tk.Tk()
    app = ClinicalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
