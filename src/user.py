"""
user.py - User class and credential management for the Clinical Data Warehouse.
"""

import csv
import os


class User:
    """Represents an authenticated system user with a role."""

    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role

    def can_access_phi(self) -> bool:
        """Return True if the user is allowed to access patient PHI."""
        return self.role in ("clinician", "nurse")

    def can_access_admin_stats(self) -> bool:
        """Return True if the user can access admin-level statistics."""
        return self.role == "admin"

    def can_access_management(self) -> bool:
        """Return True if the user is in management role."""
        return self.role == "management"

    def get_allowed_actions(self) -> list:
        """Return a list of action button labels allowed for this user's role."""
        if self.role in ("clinician", "nurse"):
            return [
                "Retrieve Patient",
                "Add Patient",
                "Remove Patient",
                "Count Visits",
                "View Note",
                "Exit",
            ]
        elif self.role == "admin":
            return [
                "Count Visits",
                "Monitor Workload",
                "Exit",
            ]
        elif self.role == "management":
            return [
                "Generate Key Statistics",
                "Monitor Revenue",
                "Exit",
            ]
        return ["Exit"]

    def __repr__(self):
        return f"User(username={self.username!r}, role={self.role!r})"


def load_credentials(filepath: str) -> dict:
    """
    Load credentials from a CSV file.

    Returns a dict mapping username -> {"password": ..., "role": ...}.
    """
    credentials = {}
    if not os.path.exists(filepath):
        return credentials

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            credentials[row["username"]] = {
                "password": row["password"],
                "role": row["role"],
            }
    return credentials


def validate_login(username: str, password: str, credentials: dict):
    """
    Validate a username/password pair against the credentials dict.

    Returns a User object on success, or None on failure.
    """
    entry = credentials.get(username)
    if entry and entry["password"] == password:
        return User(username=username, role=entry["role"])
    return None
