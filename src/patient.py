"""
patient.py - Patient data management for the Clinical Data Warehouse.
"""

import csv
import os


PATIENT_FIELDS = [
    "patient_id", "age", "gender", "bmi",
    "a1c", "bp_sys", "bp_dia", "smoking",
]


class PatientManager:
    """Handles loading, retrieving, adding, and removing patient records."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.patients = {}   # patient_id -> dict of latest record
        self._load()

    # Internal helpers

    def _load(self):
        """Read the patient CSV file into memory."""
        self.patients = {}
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row["patient_id"]
                # Keep overwriting so we naturally end up with the last row
                # (encounter-based deduplication is done in encounter.py;
                #  here we simply store one record per patient_id).
                self.patients[pid] = dict(row)

    def _save(self):
        """Write all patient records back to the CSV file."""
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=PATIENT_FIELDS)
            writer.writeheader()
            writer.writerows(self.patients.values())

    # Public API

    def retrieve(self, patient_id: str) -> dict | None:
        """Return the patient record for patient_id, or None if not found."""
        return self.patients.get(patient_id)

    def add(self, record: dict) -> tuple[bool, str]:
        """
        Add or update a patient record.

        Returns (success: bool, message: str).
        """
        pid = record.get("patient_id", "").strip()
        if not pid:
            return False, "Patient ID cannot be empty."

        if pid in self.patients:
            # Patient exists — update the record
            self.patients[pid].update(record)
            self._save()
            return True, f"Patient {pid} already existed — record updated."

        self.patients[pid] = record
        self._save()
        return True, f"Patient {pid} added successfully."

    def remove(self, patient_id: str) -> tuple[bool, str]:
        """
        Remove all records for patient_id.

        Returns (success: bool, message: str).
        """
        if patient_id not in self.patients:
            return False, f"Patient ID '{patient_id}' not found."

        del self.patients[patient_id]
        self._save()
        return True, f"Patient {patient_id} removed successfully."

    def all_ids(self) -> list:
        """Return a sorted list of all known patient IDs."""
        return sorted(self.patients.keys())

    def count(self) -> int:
        """Return the total number of patients on record."""
        return len(self.patients)
