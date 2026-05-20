"""
note.py - Clinical note management for the Clinical Data Warehouse.
"""

import csv
import os


class NoteManager:
    """Loads and queries clinical notes."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.notes = []   # list of dicts
        self._load()

    # Internal helpers

    def _load(self):
        """Read the notes CSV file into memory."""
        self.notes = []
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.notes.append(dict(row))

    # Public API

    def get_notes(self, patient_id: str, date_str: str) -> list:
        """
        Return all notes for patient_id on a given date (YYYY-MM-DD).
        """
        return [
            n for n in self.notes
            if n["patient_id"] == patient_id and n["note_date"] == date_str
        ]

    def get_all_for_patient(self, patient_id: str) -> list:
        """Return all notes for a patient sorted newest first."""
        matches = [n for n in self.notes if n["patient_id"] == patient_id]
        return sorted(matches, key=lambda n: n["note_date"], reverse=True)

    def available_dates(self, patient_id: str) -> list:
        """Return a sorted list of unique dates that have notes for a patient."""
        dates = {n["note_date"] for n in self.notes if n["patient_id"] == patient_id}
        return sorted(dates, reverse=True)
