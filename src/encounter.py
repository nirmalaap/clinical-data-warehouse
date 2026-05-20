"""
encounter.py - Encounter data management for the Clinical Data Warehouse.
"""

import csv
import os
from collections import defaultdict


class EncounterManager:
    """Loads and queries encounter records."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.encounters = []   # list of dicts
        self._load()

    # Internal helpers

    def _load(self):
        """Read the encounters CSV file into memory."""
        self.encounters = []
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.encounters.append(dict(row))

    # Public API

    def get_by_patient(self, patient_id: str) -> list:
        """Return all encounters for a given patient, sorted newest first."""
        matches = [e for e in self.encounters if e["patient_id"] == patient_id]
        return sorted(matches, key=lambda e: e["encounter_date"], reverse=True)

    def most_recent_encounter(self, patient_id: str) -> dict | None:
        """Return the single most recent encounter for a patient, or None."""
        records = self.get_by_patient(patient_id)
        return records[0] if records else None

    def count_by_date(self, date_str: str) -> int:
        """Count total encounters on a given date (YYYY-MM-DD)."""
        return sum(1 for e in self.encounters if e["encounter_date"] == date_str)

    def count_per_patient_by_date(self, date_str: str) -> dict:
        """
        Return a dict {patient_id: count} for encounters on a given date.
        """
        counts: dict = defaultdict(int)
        for e in self.encounters:
            if e["encounter_date"] == date_str:
                counts[e["patient_id"]] += 1
        return dict(counts)

    def count_by_department_on_date(self, date_str: str) -> dict:
        """
        Return a dict {department_id: count} for encounters on a given date.
        """
        counts: dict = defaultdict(int)
        for e in self.encounters:
            if e["encounter_date"] == date_str:
                counts[e["department_id"]] += 1
        return dict(counts)

    def provider_workload(self) -> list:
        """
        Return providers ranked by encounter count (descending).

        Returns a list of (provider_id, count) tuples.
        """
        counts: dict = defaultdict(int)
        for e in self.encounters:
            counts[e["provider_id"]] += 1
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return ranked

    def all_encounters(self) -> list:
        """Return the full encounter list."""
        return self.encounters
