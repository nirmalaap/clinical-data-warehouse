"""
stats.py - Statistics, revenue, and workload reporting for the Clinical Data Warehouse.
"""

import csv
import os
from collections import defaultdict


class StatsManager:
    """Generates key statistics, department revenue, and provider workload."""

    def __init__(
        self,
        patients_file: str,
        encounters_file: str,
        procedures_file: str,
        providers_file: str,
        departments_file: str,
    ):
        self.patients = self._load_csv(patients_file)
        self.encounters = self._load_csv(encounters_file)
        self.procedures = self._load_csv(procedures_file)
        self.providers = self._load_csv(providers_file)
        self.departments = self._load_csv(departments_file)

    # Internal helpers

    @staticmethod
    def _load_csv(filepath: str) -> list:
        """Load a CSV file into a list of dicts."""
        if not os.path.exists(filepath):
            return []
        with open(filepath, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def _safe_float(value: str) -> float | None:
        """Convert a string to float, returning None if blank or invalid."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    # Key statistics

    def key_statistics(self) -> dict:
        """
        Compute high-level statistics for the management dashboard.

        Returns a dict of metric -> value (or sub-dict).
        """
        stats = {}

        # Patient counts
        stats["total_patients"] = len(self.patients)
        stats["total_encounters"] = len(self.encounters)
        stats["total_procedures"] = len(self.procedures)

        # Gender breakdown
        gender_counts: dict = defaultdict(int)
        for p in self.patients:
            gender_counts[p.get("gender", "Unknown")] += 1
        stats["gender_breakdown"] = dict(gender_counts)

        # Average age
        ages = [self._safe_float(p.get("age")) for p in self.patients]
        ages = [a for a in ages if a is not None]
        stats["average_age"] = round(sum(ages) / len(ages), 1) if ages else 0

        # Average BMI
        bmis = [self._safe_float(p.get("bmi")) for p in self.patients]
        bmis = [b for b in bmis if b is not None]
        stats["average_bmi"] = round(sum(bmis) / len(bmis), 1) if bmis else 0

        # Smoking prevalence
        smokers = sum(
            1 for p in self.patients
            if str(p.get("smoking", "")).lower() in ("true", "1", "yes")
        )
        stats["smoking_rate_pct"] = (
            round(smokers / len(self.patients) * 100, 1) if self.patients else 0
        )

        # Encounter type breakdown
        enc_types: dict = defaultdict(int)
        for e in self.encounters:
            enc_types[e.get("encounter_type", "Unknown")] += 1
        stats["encounter_type_breakdown"] = dict(enc_types)

        # Department encounter counts
        dept_counts: dict = defaultdict(int)
        for e in self.encounters:
            dept_counts[e.get("department_id", "?")] += 1
        stats["encounters_by_department"] = dict(dept_counts)

        return stats

    # Revenue

    def department_revenue(self) -> list:
        """
        Compute total procedure cost per department.

        Returns a list of (dept_name, total_cost) sorted descending.
        """
        # Map encounter_id -> department_id
        enc_to_dept = {
            e["encounter_id"]: e["department_id"] for e in self.encounters
        }
        # Map department_id -> name
        dept_names = {d["department_id"]: d["name"] for d in self.departments}

        revenue: dict = defaultdict(float)
        for proc in self.procedures:
            eid = proc.get("encounter_id", "")
            dept_id = enc_to_dept.get(eid, "Unknown")
            cost = self._safe_float(proc.get("cost", "0")) or 0.0
            revenue[dept_id] += cost

        results = [
            (dept_names.get(did, did), round(total, 2))
            for did, total in revenue.items()
        ]
        return sorted(results, key=lambda x: x[1], reverse=True)

    # Workload

    def provider_workload(self) -> list:
        """
        Rank providers by number of encounters (descending).

        Returns a list of (provider_name, specialty, encounter_count) tuples.
        """
        prov_info = {
            p["provider_id"]: (p["name"], p["specialty"]) for p in self.providers
        }

        counts: dict = defaultdict(int)
        for e in self.encounters:
            counts[e.get("provider_id", "?")] += 1

        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [
            (prov_info.get(pid, (pid, "Unknown"))[0],
             prov_info.get(pid, (pid, "Unknown"))[1],
             cnt)
            for pid, cnt in ranked
        ]
