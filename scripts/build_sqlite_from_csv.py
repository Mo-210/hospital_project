"""
Build a SQLite database from the CSV extracts in data/.

This script is the reproducible bridge between flat files and SQL analytics.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "hospital.db"


DDL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS treatments;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT,
    date_of_birth TEXT,
    contact_number TEXT,
    address TEXT,
    registration_date TEXT,
    insurance_provider TEXT,
    insurance_number TEXT,
    email TEXT
);

CREATE TABLE doctors (
    doctor_id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    specialization TEXT,
    phone_number TEXT,
    years_experience INTEGER,
    hospital_branch TEXT,
    email TEXT
);

CREATE TABLE appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT,
    doctor_id TEXT,
    appointment_date TEXT,
    appointment_time TEXT,
    reason_for_visit TEXT,
    status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE treatments (
    treatment_id TEXT PRIMARY KEY,
    appointment_id TEXT,
    treatment_type TEXT,
    description TEXT,
    cost REAL,
    treatment_date TEXT,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE billing (
    bill_id TEXT PRIMARY KEY,
    patient_id TEXT,
    treatment_id TEXT,
    bill_date TEXT,
    amount REAL,
    payment_method TEXT,
    payment_status TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (treatment_id) REFERENCES treatments(treatment_id)
);
"""


def build_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    patients = pd.read_csv(DATA_DIR / "patients.csv")
    doctors = pd.read_csv(DATA_DIR / "doctors.csv")
    appointments = pd.read_csv(DATA_DIR / "appointments.csv")
    treatments = pd.read_csv(DATA_DIR / "treatments.csv")
    billing = pd.read_csv(DATA_DIR / "billing.csv")

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(DDL)
        patients.to_sql("patients", conn, if_exists="append", index=False)
        doctors.to_sql("doctors", conn, if_exists="append", index=False)
        appointments.to_sql("appointments", conn, if_exists="append", index=False)
        treatments.to_sql("treatments", conn, if_exists="append", index=False)
        billing.to_sql("billing", conn, if_exists="append", index=False)
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build SQLite DB from CSV files in data/.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Output SQLite path (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args()

    build_database(args.db_path)
    print(f"SQLite database created at: {args.db_path.resolve()}")


if __name__ == "__main__":
    main()
