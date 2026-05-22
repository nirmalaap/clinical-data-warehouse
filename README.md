# Clinical Data Warehouse — HI 741 Final Project

Author: Nirmala Arimala Paramasivam

Course: HI 741 Spring 2026

A Tkinter-based desktop application for managing a hospital clinical data warehouse. Users log in with role-based credentials and can perform patient management, visit tracking, clinical note viewing, and administrative reporting.

\## 🔗 GitHub Repository

https://github.com/nirmalaap/clinical-data-warehouse



\---

\---

## 📁 Project Structure

```
Nirmala.Arimalaparamasivam.Project/
├── main.py                  # Entry point — run this file
├── requirements.txt         # Python dependencies
├── README.md
│
├── src/
│   ├── ui.py                # Tkinter UI application class
│   ├── user.py              # User class \& credential validation
│   ├── patient.py           # PatientManager — add/remove/retrieve
│   ├── encounter.py         # EncounterManager — visit queries
│   ├── note.py              # NoteManager — clinical notes
│   ├── stats.py             # StatsManager — statistics/revenue/workload
│   └── logger.py            # UsageLogger — login \\\& action logging
│
├── Data/
│   ├── credentials.csv      # User login credentials
│   ├── patients.csv         # Patient records
│   ├── encounters.csv       # Encounter records
│   ├── notes.csv            # Clinical notes
│   ├── procedures.csv       # Procedures and costs
│   ├── providers.csv        # Provider information
│   └── departments.csv      # Department information
│
└── outputs/
    ├── patients.csv         # Updated patient file (after add/remove)
    └── usage\_log.csv        # Login and action history
```

\---

## ⚙️ Requirements

* Python 3.10 or higher
* `tkinter` (included with standard Python on Windows)
* No additional third-party packages required

\---

## 🚀 How to Run

### Step 1 — Generate the data (first time only)

```bash
python data\\\_generator.py
```

Move the generated `.csv` files into the `Data/` folder.

### Step 2 — Run the application

```bash
python main.py
```

The login window will appear. Use the credentials below.

\---

## 🔑 Sample Login Credentials

|Username|Password|Role|
|-|-|-|
|alice|pass123|clinician|
|nina|pass201|nurse|
|dave|pass000|admin|
|carol|pass789|management|

\---

## 👥 User Roles \& Permissions

|Role|Allowed Actions|
|-|-|
|clinician|Retrieve / Add / Remove Patient, Count Visits, View Note|
|nurse|Retrieve / Add / Remove Patient, Count Visits, View Note|
|admin|Count Visits, Monitor Provider Workload|
|management|Generate Key Statistics, Monitor Department Revenue|

\---

## 📋 Features

1. **Login** — Credential validation with role-based menus
2. **Retrieve Patient** — Search by Patient ID; shows most recent encounter
3. **Add Patient** — Form with dropdowns for categorical fields; updates file
4. **Remove Patient** — Removes all records for a Patient ID; updates file
5. **Count Visits** — Count encounters by date; breakdowns by patient or dept
6. **View Note** — View clinical notes for a patient on a specific date
7. **Generate Key Statistics** — Summary stats for management
8. **Monitor Revenue** — Total procedure revenue per department
9. **Monitor Workload** — Provider encounter rankings
10. **Usage Logging** — Every login and action is recorded to `outputs/usage\\\_log.csv`

\---

## 📝 Notes for Developers

* All business logic is separated into dedicated modules under `src/`.
* `main.py` is the only file intended to be executed directly.
* The `outputs/usage\\\_log.csv` file is created automatically on first run.
* Data files are read with relative paths; do not hard-code absolute paths.



Tested and verified working on Windows.

