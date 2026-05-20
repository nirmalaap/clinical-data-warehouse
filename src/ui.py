"""
ui.py - Tkinter UI for the Clinical Data Warehouse.

Provides login, role-based menus, and all 8 essential actions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import random

from user import load_credentials, validate_login
from patient import PatientManager
from encounter import EncounterManager
from note import NoteManager
from stats import StatsManager
from logger import UsageLogger

# Paths (relative to the project root, i.e. one level above src/)
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_DIR = os.path.join(BASE_DIR, "Data")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

CRED_FILE = os.path.join(DATA_DIR, "credentials.csv")
PATIENT_FILE = os.path.join(DATA_DIR, "patients.csv")
ENCOUNTER_FILE = os.path.join(DATA_DIR, "encounters.csv")
NOTE_FILE = os.path.join(DATA_DIR, "notes.csv")
PROCEDURE_FILE = os.path.join(DATA_DIR, "procedures.csv")
PROVIDER_FILE = os.path.join(DATA_DIR, "providers.csv")
DEPARTMENT_FILE = os.path.join(DATA_DIR, "departments.csv")
LOG_FILE = os.path.join(OUT_DIR, "usage_log.csv")

# Colour palette
BG = "#f0f4f8"
HEADER_BG = "#1a3c5e"
HEADER_FG = "#ffffff"
BTN_BG = "#2e6da4"
BTN_FG = "#ffffff"
BTN_ACTIVE = "#1a4f7a"
DANGER_BG = "#c0392b"
SUCCESS_BG = "#27ae60"
FONT_BODY = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 9)


# Helper widgets

def _make_button(parent, text, command, bg=BTN_BG, fg=BTN_FG, width=22):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=BTN_ACTIVE, activeforeground=fg,
        font=FONT_BODY, relief="flat", padx=8, pady=6, width=width,
        cursor="hand2",
    )
    return btn


def _make_label(parent, text, font=FONT_BODY, fg="#1a1a2e", **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=BG, **kw)


def _make_entry(parent, show=None):
    e = tk.Entry(parent, font=FONT_BODY, show=show, relief="solid", bd=1)
    return e


# Main Application

class ClinicalApp:
    """
    Root Tkinter application for the Clinical Data Warehouse UI.

    Manages frame transitions between Login, Menu, and Action screens.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Clinical Data Warehouse")
        self.root.geometry("750x580")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        # Ensure outputs directory exists
        os.makedirs(OUT_DIR, exist_ok=True)

        # Load data managers
        self.credentials = load_credentials(CRED_FILE)
        self.patient_mgr = PatientManager(PATIENT_FILE)
        self.encounter_mgr = EncounterManager(ENCOUNTER_FILE)
        self.note_mgr = NoteManager(NOTE_FILE)
        self.stats_mgr = StatsManager(
            PATIENT_FILE, ENCOUNTER_FILE, PROCEDURE_FILE,
            PROVIDER_FILE, DEPARTMENT_FILE,
        )
        self.logger = UsageLogger(LOG_FILE)

        self.current_user = None
        self.current_frame = None

        self._show_login()

    # Frame management

    def _clear(self):
        """Destroy the currently displayed frame."""
        if self.current_frame:
            self.current_frame.destroy()

    def _base_frame(self) -> tk.Frame:
        """Create and return a fresh content frame."""
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        return frame

    def _header(self, parent, title: str):
        """Render a branded header bar."""
        bar = tk.Frame(parent, bg=HEADER_BG)
        bar.pack(fill="x")
        tk.Label(
            bar, text="🏥  Clinical Data Warehouse", font=("Segoe UI", 12, "bold"),
            bg=HEADER_BG, fg=HEADER_FG, pady=8,
        ).pack(side="left", padx=14)
        tk.Label(
            bar, text=title, font=("Segoe UI", 12),
            bg=HEADER_BG, fg="#aecde8", pady=8,
        ).pack(side="right", padx=14)

    # Login screen

    def _show_login(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Login")

        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        tk.Label(body, text="Clinical Data Warehouse", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=HEADER_BG).grid(row=0, column=0, columnspan=2, pady=(30, 4))
        tk.Label(body, text="Please log in to continue", font=FONT_SMALL,
                 bg=BG, fg="#666").grid(row=1, column=0, columnspan=2, pady=(0, 24))

        _make_label(body, "Username:").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self._entry_user = _make_entry(body)
        self._entry_user.grid(row=2, column=1, pady=6, ipadx=40)

        _make_label(body, "Password:").grid(row=3, column=0, sticky="e", padx=8, pady=6)
        self._entry_pass = _make_entry(body, show="*")
        self._entry_pass.grid(row=3, column=1, pady=6, ipadx=40)

        # Bind Enter key
        self._entry_pass.bind("<Return>", lambda e: self._do_login())
        self._entry_user.bind("<Return>", lambda e: self._entry_pass.focus())

        btn = _make_button(body, "Log In", self._do_login, width=18)
        btn.grid(row=4, column=0, columnspan=2, pady=18)

        self._entry_user.focus()

    def _do_login(self):
        username = self._entry_user.get().strip()
        password = self._entry_pass.get().strip()

        user = validate_login(username, password, self.credentials)
        if user:
            self.logger.log_login(username, user.role, success=True)
            self.current_user = user
            self._show_menu()
        else:
            self.logger.log_login(username, "", success=False)
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password. Please try again."
            )
            self._entry_pass.delete(0, "end")

    # Role-based menu

    def _show_menu(self):
        self._clear()
        frame = self._base_frame()
        u = self.current_user
        self._header(frame, f"Logged in as: {u.username}  [{u.role}]")

        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        _make_label(body, f"Welcome, {u.username}!", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(28, 4))
        _make_label(body, f"Role: {u.role.title()}",
                    font=FONT_SMALL, fg="#555").pack(pady=(0, 20))

        action_map = {
            "Retrieve Patient": self._show_retrieve,
            "Add Patient": self._show_add,
            "Remove Patient": self._show_remove,
            "Count Visits": self._show_count_visits,
            "View Note": self._show_view_note,
            "Generate Key Statistics": self._show_statistics,
            "Monitor Revenue": self._show_revenue,
            "Monitor Workload": self._show_workload,
            "Exit": self._do_exit,
        }

        btn_frame = tk.Frame(body, bg=BG)
        btn_frame.pack()

        for i, label in enumerate(u.get_allowed_actions()):
            bg = DANGER_BG if label == "Exit" else BTN_BG
            cmd = action_map.get(label, lambda: None)
            btn = _make_button(btn_frame, label, cmd, bg=bg, width=24)
            btn.grid(row=i // 2, column=i % 2, padx=12, pady=8)

    # Shared helpers

    def _back_button(self, parent):
        _make_button(parent, "← Back to Menu", self._show_menu,
                     bg="#6c757d", width=18).pack(pady=12)

    def _result_box(self, parent, text: str):
        """Show a scrollable read-only result box."""
        box = scrolledtext.ScrolledText(
            parent, font=("Courier New", 10), wrap="word",
            height=14, width=72, relief="solid", bd=1,
        )
        box.insert("1.0", text)
        box.configure(state="disabled")
        box.pack(padx=16, pady=8)
        return box

    def _log(self, action: str):
        u = self.current_user
        self.logger.log_action(u.username, u.role, action)

    # Action: Retrieve Patient

    def _show_retrieve(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Retrieve Patient")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        _make_label(body, "Retrieve Patient", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(24, 12))
        _make_label(body, "Enter Patient ID:").pack()
        entry = _make_entry(body)
        entry.pack(pady=6, ipadx=30)
        entry.focus()

        def search():
            pid = entry.get().strip()
            rec = self.patient_mgr.retrieve(pid)
            if rec is None:
                messagebox.showwarning("Not Found", f"Patient '{pid}' not found.")
                return
            # Also get most recent encounter
            enc = self.encounter_mgr.most_recent_encounter(pid)
            lines = ["=== Patient Record ===\n"]
            for k, v in rec.items():
                lines.append(f"  {k:<14}: {v}")
            if enc:
                lines.append("\n=== Most Recent Encounter ===")
                for k, v in enc.items():
                    lines.append(f"  {k:<20}: {v}")
            self._log(f"Retrieve Patient {pid}")
            result_frame = tk.Toplevel(self.root)
            result_frame.title(f"Patient {pid}")
            result_frame.configure(bg=BG)
            result_frame.geometry("520x380")
            st = scrolledtext.ScrolledText(result_frame, font=("Courier New", 10),
                                           wrap="word", relief="solid", bd=1)
            st.pack(fill="both", expand=True, padx=12, pady=12)
            st.insert("1.0", "\n".join(lines))
            st.configure(state="disabled")

        _make_button(body, "Search", search).pack(pady=10)
        self._back_button(body)

    # Action: Add Patient

    def _show_add(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Add Patient")

        canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        _make_label(body, "Add / Update Patient", font=FONT_TITLE,
                    fg=HEADER_BG).grid(row=0, column=0, columnspan=2, pady=(18, 12))

        fields = [
            ("Patient ID *", "patient_id", "entry", None),
            ("Age", "age", "entry", None),
            ("Gender", "gender", "combo", ["Male", "Female", "Non-binary"]),
            ("BMI", "bmi", "entry", None),
            ("A1C Level", "a1c", "entry", None),
            ("Systolic BP", "bp_sys", "entry", None),
            ("Diastolic BP", "bp_dia", "entry", None),
            ("Smoker", "smoking", "combo", ["True", "False"]),
        ]

        widgets = {}
        for i, (label, key, wtype, opts) in enumerate(fields, start=1):
            _make_label(body, label + ":").grid(row=i, column=0, sticky="e",
                                                padx=10, pady=5)
            if wtype == "entry":
                w = _make_entry(body)
                w.grid(row=i, column=1, padx=10, pady=5, ipadx=30)
            else:
                var = tk.StringVar(value=opts[0])
                w = ttk.Combobox(body, textvariable=var, values=opts,
                                 state="readonly", font=FONT_BODY, width=18)
                w.grid(row=i, column=1, padx=10, pady=5)
                w = var   # store the StringVar
            widgets[key] = w

        def submit():
            record = {}
            for key, w in widgets.items():
                val = w.get() if isinstance(w, tk.StringVar) else w.get()
                record[key] = val.strip()
            ok, msg = self.patient_mgr.add(record)
            if ok:
                self._log(f"Add Patient {record.get('patient_id', '')}")
                messagebox.showinfo("Success", msg)
                self._show_menu()
            else:
                messagebox.showerror("Error", msg)

        row_count = len(fields) + 1
        _make_button(body, "Submit", submit, bg=SUCCESS_BG).grid(
            row=row_count, column=0, columnspan=2, pady=14)
        _make_button(body, "← Back to Menu", self._show_menu,
                     bg="#6c757d", width=18).grid(
            row=row_count + 1, column=0, columnspan=2, pady=4)

    # Action: Remove Patient

    def _show_remove(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Remove Patient")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        _make_label(body, "Remove Patient", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(24, 12))
        _make_label(body, "Enter Patient ID to remove:").pack()
        entry = _make_entry(body)
        entry.pack(pady=6, ipadx=30)
        entry.focus()

        def remove():
            pid = entry.get().strip()
            if not pid:
                messagebox.showwarning("Input Error", "Please enter a Patient ID.")
                return
            confirm = messagebox.askyesno(
                "Confirm Removal",
                f"Are you sure you want to remove ALL records for patient '{pid}'?"
            )
            if not confirm:
                return
            ok, msg = self.patient_mgr.remove(pid)
            if ok:
                self._log(f"Remove Patient {pid}")
                messagebox.showinfo("Removed", msg)
                self._show_menu()
            else:
                messagebox.showerror("Not Found", msg)

        _make_button(body, "Remove", remove, bg=DANGER_BG).pack(pady=10)
        self._back_button(body)

    # Action: Count Visits
    # ------------------------------------------------------------------

    def _show_count_visits(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Count Visits")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        _make_label(body, "Count Visits", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(24, 12))
        _make_label(body, "Enter Date (YYYY-MM-DD):").pack()
        entry_date = _make_entry(body)
        entry_date.pack(pady=6, ipadx=30)
        entry_date.focus()

        _make_label(body, "View breakdown by:").pack(pady=(10, 2))
        mode_var = tk.StringVar(value="total")
        modes = [("Total only", "total"),
                 ("Per patient", "patient"),
                 ("By department", "dept")]
        for txt, val in modes:
            tk.Radiobutton(body, text=txt, variable=mode_var, value=val,
                           bg=BG, font=FONT_BODY).pack()

        def count():
            date = entry_date.get().strip()
            if not date:
                messagebox.showwarning("Input Error", "Please enter a date.")
                return
            mode = mode_var.get()
            lines = [f"Visits on {date}\n{'='*36}\n"]
            if mode == "total":
                total = self.encounter_mgr.count_by_date(date)
                lines.append(f"Total encounters: {total}")
            elif mode == "patient":
                data = self.encounter_mgr.count_per_patient_by_date(date)
                if not data:
                    lines.append("No encounters found.")
                for pid, cnt in sorted(data.items()):
                    lines.append(f"  {pid}: {cnt} visit(s)")
                lines.append(f"\nTotal: {sum(data.values())}")
            else:
                data = self.encounter_mgr.count_by_department_on_date(date)
                if not data:
                    lines.append("No encounters found.")
                for dept, cnt in sorted(data.items()):
                    lines.append(f"  {dept}: {cnt} encounter(s)")
                lines.append(f"\nTotal: {sum(data.values())}")

            self._log(f"Count Visits {date} ({mode})")
            popup = tk.Toplevel(self.root)
            popup.title(f"Visits on {date}")
            popup.geometry("460x320")
            popup.configure(bg=BG)
            st = scrolledtext.ScrolledText(popup, font=("Courier New", 10),
                                           wrap="word", relief="solid", bd=1)
            st.pack(fill="both", expand=True, padx=12, pady=12)
            st.insert("1.0", "\n".join(lines))
            st.configure(state="disabled")

        _make_button(body, "Count", count).pack(pady=14)
        self._back_button(body)

    # Action: View Note

    def _show_view_note(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "View Clinical Note")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True)

        _make_label(body, "View Clinical Note", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(24, 12))

        row1 = tk.Frame(body, bg=BG)
        row1.pack(pady=4)
        _make_label(row1, "Patient ID:").pack(side="left", padx=6)
        entry_pid = _make_entry(row1)
        entry_pid.pack(side="left", ipadx=20)
        entry_pid.focus()

        row2 = tk.Frame(body, bg=BG)
        row2.pack(pady=4)
        _make_label(row2, "Date (YYYY-MM-DD):").pack(side="left", padx=6)
        entry_date = _make_entry(row2)
        entry_date.pack(side="left", ipadx=20)

        def view():
            pid = entry_pid.get().strip()
            date = entry_date.get().strip()
            notes = self.note_mgr.get_notes(pid, date)
            if not notes:
                messagebox.showwarning(
                    "Not Found",
                    f"No notes found for patient '{pid}' on {date}."
                )
                return
            lines = [f"Clinical Notes — Patient {pid}  Date: {date}\n{'='*50}\n"]
            for n in notes:
                lines.append(f"Note ID   : {n['note_id']}")
                lines.append(f"Type      : {n['note_type']}")
                lines.append(f"Encounter : {n['encounter_id']}")
                lines.append(f"\n{n['note_text']}\n")
                lines.append("-" * 50)
            self._log(f"View Note Patient {pid} Date {date}")
            popup = tk.Toplevel(self.root)
            popup.title(f"Notes — {pid} on {date}")
            popup.geometry("560x380")
            popup.configure(bg=BG)
            st = scrolledtext.ScrolledText(popup, font=("Courier New", 10),
                                           wrap="word", relief="solid", bd=1)
            st.pack(fill="both", expand=True, padx=12, pady=12)
            st.insert("1.0", "\n".join(lines))
            st.configure(state="disabled")

        _make_button(body, "View Note", view).pack(pady=14)
        self._back_button(body)

    # Action: Generate Key Statistics

    def _show_statistics(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Key Statistics")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True, fill="both")

        _make_label(body, "Key Statistics", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(20, 10))

        stats = self.stats_mgr.key_statistics()
        lines = ["=== Clinical Data Warehouse — Key Statistics ===\n"]
        lines.append(f"Total Patients       : {stats['total_patients']}")
        lines.append(f"Total Encounters     : {stats['total_encounters']}")
        lines.append(f"Total Procedures     : {stats['total_procedures']}")
        lines.append(f"Average Patient Age  : {stats['average_age']}")
        lines.append(f"Average BMI          : {stats['average_bmi']}")
        lines.append(f"Smoking Rate         : {stats['smoking_rate_pct']}%")
        lines.append("\n--- Gender Breakdown ---")
        for g, cnt in stats["gender_breakdown"].items():
            lines.append(f"  {g:<14}: {cnt}")
        lines.append("\n--- Encounter Types ---")
        for t, cnt in stats["encounter_type_breakdown"].items():
            lines.append(f"  {t:<20}: {cnt}")
        lines.append("\n--- Encounters by Department ---")
        for d, cnt in stats["encounters_by_department"].items():
            lines.append(f"  {d:<8}: {cnt}")

        self._result_box(body, "\n".join(lines))
        self._log("Generate Key Statistics")
        self._back_button(body)

    # Action: Monitor Revenue

    def _show_revenue(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Department Revenue")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True, fill="both")

        _make_label(body, "Department Revenue", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(20, 10))

        revenue = self.stats_mgr.department_revenue()
        lines = ["=== Total Procedure Revenue by Department ===\n"]
        lines.append(f"{'Department':<25} {'Revenue':>12}")
        lines.append("-" * 38)
        for name, total in revenue:
            lines.append(f"{name:<25} ${total:>11,.2f}")
        grand = sum(t for _, t in revenue)
        lines.append("-" * 38)
        lines.append(f"{'TOTAL':<25} ${grand:>11,.2f}")

        self._result_box(body, "\n".join(lines))
        self._log("Monitor Revenue")
        self._back_button(body)

    # Action: Monitor Workload

    def _show_workload(self):
        self._clear()
        frame = self._base_frame()
        self._header(frame, "Provider Workload")
        body = tk.Frame(frame, bg=BG)
        body.pack(expand=True, fill="both")

        _make_label(body, "Provider Workload", font=FONT_TITLE,
                    fg=HEADER_BG).pack(pady=(20, 10))

        workload = self.stats_mgr.provider_workload()
        lines = ["=== Provider Workload (Ranked by Encounters) ===\n"]
        lines.append(f"{'Rank':<6} {'Name':<12} {'Specialty':<22} {'Encounters':>10}")
        lines.append("-" * 52)
        for rank, (name, specialty, cnt) in enumerate(workload, start=1):
            lines.append(f"{rank:<6} {name:<12} {specialty:<22} {cnt:>10}")

        self._result_box(body, "\n".join(lines))
        self._log("Monitor Workload")
        self._back_button(body)

    # Exit

    def _do_exit(self):
        u = self.current_user
        if u:
            self.logger.log_logout(u.username, u.role)
        self.root.quit()
        self.root.destroy()
