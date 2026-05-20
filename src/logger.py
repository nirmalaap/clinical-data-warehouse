"""
logger.py - Usage logging for the Clinical Data Warehouse.

Records every login attempt and every action performed by users.
Output is a human-readable CSV file.
"""

import csv
import os
from datetime import datetime


LOG_FIELDS = ["timestamp", "username", "role", "action", "status"]


class UsageLogger:
    """Appends usage events to a persistent CSV log file."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_file()

    # Internal helpers

    def _ensure_file(self):
        """Create the log file with a header row if it does not yet exist."""
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
                writer.writeheader()

    def _write(self, row: dict):
        """Append a single row to the log file."""
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
            writer.writerow(row)

    # Public API

    def log_login(self, username: str, role: str, success: bool):
        """
        Record a login attempt.

        Parameters
        ----------
        username : str
        role     : str  — the role if known, else empty string
        success  : bool — True = successful login, False = failed attempt
        """
        self._write({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "role": role,
            "action": "LOGIN",
            "status": "SUCCESS" if success else "FAILED",
        })

    def log_action(self, username: str, role: str, action: str):
        """
        Record an action performed by a logged-in user.

        Parameters
        ----------
        username : str
        role     : str
        action   : str — description of the action (e.g. "Retrieve Patient P3")
        """
        self._write({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "role": role,
            "action": action,
            "status": "PERFORMED",
        })

    def log_logout(self, username: str, role: str):
        """Record that a user exited/logged out."""
        self._write({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "role": role,
            "action": "LOGOUT",
            "status": "SUCCESS",
        })
