"""
Database module - SQLite storage for AgriDoc AI.

Schema:
- diseases: Encyclopedia entries (plant, disease, symptoms, causes, etc.)
- diagnosis_history: Historical diagnosis records with timestamps
"""
import os
import json
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "agridoc.db")
JSON_BACKUP_PATH = os.path.join(os.path.dirname(__file__), "encyclopedia.json.bak")


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent read performance
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS diseases (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plant TEXT NOT NULL,
            symptoms TEXT DEFAULT '',
            causes TEXT DEFAULT '',
            harm TEXT DEFAULT '',
            treatment TEXT DEFAULT '',
            recovery_time TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id TEXT NOT NULL,
            disease_name TEXT NOT NULL,
            plant_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            is_healthy INTEGER DEFAULT 0,
            image_filename TEXT DEFAULT '',
            diagnosed_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (disease_id) REFERENCES diseases(id)
        );

        CREATE INDEX IF NOT EXISTS idx_history_date ON diagnosis_history(diagnosed_at);
        CREATE INDEX IF NOT EXISTS idx_history_disease ON diagnosis_history(disease_id);
    """)

    conn.commit()
    conn.close()


def migrate_from_json(json_path: str):
    """
    Migrate existing encyclopedia.json data into SQLite.
    Backs up the JSON file before migration.
    """
    if not os.path.exists(json_path):
        print(f"[DB Migration] No JSON file found at {json_path}, skipping migration.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        diseases = json.load(f)

    if not diseases:
        return

    conn = get_connection()
    cursor = conn.cursor()
    migrated = 0
    skipped = 0

    for d in diseases:
        disease_id = d.get("id", "")
        if not disease_id:
            continue

        # Check if already exists
        existing = cursor.execute("SELECT id FROM diseases WHERE id = ?", (disease_id,)).fetchone()
        if existing:
            skipped += 1
            continue

        cursor.execute(
            """INSERT INTO diseases (id, name, plant, symptoms, causes, harm, treatment, recovery_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                disease_id,
                d.get("name", ""),
                d.get("plant", ""),
                d.get("symptoms", ""),
                d.get("causes", ""),
                d.get("harm", ""),
                d.get("treatment", ""),
                d.get("recovery_time", ""),
            )
        )
        migrated += 1

    conn.commit()
    conn.close()

    # Backup original JSON
    import shutil
    backup_path = json_path + ".bak"
    shutil.copy2(json_path, backup_path)

    print(f"[DB Migration] Done: {migrated} migrated, {skipped} skipped (already exist). Backup: {backup_path}")


# --- Disease CRUD Operations ---

def get_all_diseases() -> list:
    """Get all disease entries as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM diseases ORDER BY plant, name").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_disease_by_id(disease_id: str) -> dict | None:
    """Get a single disease entry by its ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM diseases WHERE id = ?", (disease_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_disease(disease_data: dict):
    """Insert or update a disease entry."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO diseases (id, name, plant, symptoms, causes, harm, treatment, recovery_time, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
           ON CONFLICT(id) DO UPDATE SET
             name = excluded.name,
             plant = excluded.plant,
             symptoms = excluded.symptoms,
             causes = excluded.causes,
             harm = excluded.harm,
             treatment = excluded.treatment,
             recovery_time = excluded.recovery_time,
             updated_at = datetime('now')""",
        (
            disease_data.get("id", ""),
            disease_data.get("name", ""),
            disease_data.get("plant", ""),
            disease_data.get("symptoms", ""),
            disease_data.get("causes", ""),
            disease_data.get("harm", ""),
            disease_data.get("treatment", ""),
            disease_data.get("recovery_time", ""),
        )
    )
    conn.commit()
    conn.close()


def update_disease_fields(disease_id: str, fields: dict):
    """Update specific fields of a disease entry."""
    conn = get_connection()
    # Build dynamic SET clause
    allowed = {'name', 'plant', 'symptoms', 'causes', 'harm', 'treatment', 'recovery_time'}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        conn.close()
        return

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [disease_id]

    conn.execute(
        f"UPDATE diseases SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


# --- Diagnosis History Operations ---

def add_diagnosis_record(disease_id: str, disease_name: str, plant_name: str,
                         confidence: float, is_healthy: bool, image_filename: str = ""):
    """Record a diagnosis result in history."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO diagnosis_history (disease_id, disease_name, plant_name, confidence, is_healthy, image_filename)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (disease_id, disease_name, plant_name, confidence, int(is_healthy), image_filename)
    )
    conn.commit()
    conn.close()


def get_diagnosis_history(limit: int = 50, offset: int = 0) -> list:
    """Get diagnosis history, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM diagnosis_history
           ORDER BY diagnosed_at DESC
           LIMIT ? OFFSET ?""",
        (limit, offset)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_diagnosis_stats() -> dict:
    """Get summary statistics for the diagnosis history."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM diagnosis_history").fetchone()["c"]
    diseased = conn.execute("SELECT COUNT(*) as c FROM diagnosis_history WHERE is_healthy = 0").fetchone()["c"]
    healthy = conn.execute("SELECT COUNT(*) as c FROM diagnosis_history WHERE is_healthy = 1").fetchone()["c"]

    # Top 5 most diagnosed diseases
    top_diseases = conn.execute(
        """SELECT disease_name, plant_name, COUNT(*) as count
           FROM diagnosis_history
           WHERE is_healthy = 0
           GROUP BY disease_id
           ORDER BY count DESC
           LIMIT 5"""
    ).fetchall()

    conn.close()
    return {
        "total_diagnoses": total,
        "diseased_count": diseased,
        "healthy_count": healthy,
        "top_diseases": [dict(r) for r in top_diseases],
    }


# Initialize DB on module import
init_db()
