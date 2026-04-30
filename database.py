"""
SQLite persistence layer for the Digital Consulting Engineer (v2).

Schema changes vs v1:

* `checklist_items.status` is now a TEXT enum
  (PENDING / PASS / FAIL / REWORK) to support the **Rework Loop**.
* `checklist_items.rework_count` tracks how many retries an item has had.
* New `materials` table for the **Material Delivery Gate** — invoices are
  uploaded and matched against the AI-generated BOQ before the related
  checklist item is allowed to PASS.
* New `payment_certificates` table — every approved phase auto-generates a
  certificate authorising the milestone payment.
* New `timers` table for **SBC Smart Timers** (curing, deshuttering).
* New `siteprep_photos` table for Phase-0 fencing & municipality board
  proofs.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Iterable

DB_PATH = "construction_app_v2.db"

# Status enum values stored in checklist_items.status
STATUS_PENDING = "PENDING"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_REWORK = "REWORK"

# Material match enum
MATCH_PENDING = "PENDING"
MATCH_OK = "MATCH"
MATCH_BAD = "MISMATCH"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                budget        REAL    DEFAULT 0,
                current_phase INTEGER DEFAULT 0,
                location      TEXT    DEFAULT '',
                created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS phase_status (
                project_id    INTEGER NOT NULL,
                phase_number  INTEGER NOT NULL,
                completed     INTEGER DEFAULT 0,
                completed_at  TEXT,
                PRIMARY KEY(project_id, phase_number),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS checklist_items (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id    INTEGER NOT NULL,
                phase_number  INTEGER NOT NULL,
                item_key      TEXT    NOT NULL,
                status        TEXT    DEFAULT 'PENDING',  -- PENDING/PASS/FAIL/REWORK
                notes         TEXT    DEFAULT '',
                image_path    TEXT,
                rework_count  INTEGER DEFAULT 0,
                updated_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, phase_number, item_key),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS boq_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL,
                item_name   TEXT    NOT NULL,
                quantity    REAL,
                unit        TEXT,
                category    TEXT    DEFAULT 'structural',
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS contracts (
                project_id       INTEGER PRIMARY KEY,
                file_path        TEXT,
                risks_accepted   INTEGER DEFAULT 0,
                missing_clauses  TEXT,
                skipped          INTEGER DEFAULT 0,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS blueprints (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL,
                file_path   TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS siteprep_photos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id  INTEGER NOT NULL,
                kind        TEXT    NOT NULL,            -- 'fencing' | 'board'
                file_path   TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, kind),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS materials (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER NOT NULL,
                phase_number    INTEGER NOT NULL,
                material_key    TEXT    NOT NULL,
                material_name   TEXT,
                expected_qty    REAL,
                expected_unit   TEXT,
                delivered_qty   REAL,
                invoice_path    TEXT,
                match_status    TEXT    DEFAULT 'PENDING',   -- PENDING/MATCH/MISMATCH
                notes           TEXT,
                delivered_at    TEXT,
                UNIQUE(project_id, phase_number, material_key),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS financials (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER NOT NULL,
                phase_number    INTEGER NOT NULL,
                milestone_name  TEXT,
                percentage      REAL,
                paid            INTEGER DEFAULT 0,
                paid_at         TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS payment_certificates (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER NOT NULL,
                phase_number    INTEGER NOT NULL,
                certificate_no  TEXT NOT NULL,
                percentage      REAL,
                amount          REAL,
                file_path       TEXT,
                issued_at       TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS timers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id      INTEGER NOT NULL,
                phase_number    INTEGER NOT NULL,
                timer_key       TEXT    NOT NULL,
                label           TEXT,
                started_at      TEXT DEFAULT CURRENT_TIMESTAMP,
                duration_seconds INTEGER,
                completed       INTEGER DEFAULT 0,
                UNIQUE(project_id, phase_number, timer_key),
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            );
            """
        )
        _run_migrations(conn)


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Idempotent column-add migrations for users upgrading from older builds.

    SQLite raises if you ALTER TABLE ADD COLUMN twice, so we check first.
    """
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(boq_items)").fetchall()}
    if "category" not in cols:
        conn.execute("ALTER TABLE boq_items ADD COLUMN category TEXT DEFAULT 'structural'")

    cols = {r["name"] for r in conn.execute("PRAGMA table_info(contracts)").fetchall()}
    if "skipped" not in cols:
        conn.execute("ALTER TABLE contracts ADD COLUMN skipped INTEGER DEFAULT 0")


# ================================ Projects =================================
def create_project(name: str, budget: float, location: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO projects(name, budget, location) VALUES (?, ?, ?)",
            (name, budget, location),
        )
        return cur.lastrowid


def list_projects() -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM projects ORDER BY id DESC"
        ).fetchall()]


def get_project(pid: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
        return dict(row) if row else None


def update_current_phase(pid: int, phase: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE projects SET current_phase=? WHERE id=?", (phase, pid)
        )


def delete_project(pid: int) -> None:
    """Delete a project and ALL its related data.

    The schema uses ON DELETE CASCADE on every child table, so a single
    DELETE on the parent row removes:
      * checklist_items, phase_status, boq_items, contracts,
      * blueprints, siteprep_photos, materials, financials,
      * payment_certificates, timers
    Uploaded files on disk are intentionally left in place (in
    ``uploads/project_<id>/``) so an admin can audit them later if needed.
    """
    with get_conn() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (pid,))


# ============================ Phase status =================================
def mark_phase_complete(project_id: int, phase: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO phase_status"
            "(project_id, phase_number, completed, completed_at) "
            "VALUES (?, ?, 1, ?)",
            (project_id, phase,
             datetime.utcnow().isoformat(timespec="seconds")),
        )


def is_phase_marked_complete(project_id: int, phase: int) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT completed FROM phase_status "
            "WHERE project_id=? AND phase_number=?",
            (project_id, phase),
        ).fetchone()
        return bool(row and row["completed"])


# ============================ Checklist ====================================
def upsert_checklist_item(
    project_id: int,
    phase: int,
    item_key: str,
    status: str | None = None,
    notes: str | None = None,
    image_path: str | None = None,
    rework_count: int | None = None,
) -> None:
    """Insert or partially update a checklist item.
    Only non-None fields are written, so callers can patch one field at a time."""
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM checklist_items "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            (project_id, phase, item_key),
        ).fetchone()

        if existing is None:
            conn.execute(
                "INSERT INTO checklist_items"
                "(project_id, phase_number, item_key, status, notes, image_path, "
                " rework_count, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    project_id, phase, item_key,
                    status or STATUS_PENDING,
                    notes or "",
                    image_path,
                    rework_count or 0,
                    now,
                ),
            )
            return

        sets, params = [], []
        if status is not None:
            sets.append("status=?"); params.append(status)
        if notes is not None:
            sets.append("notes=?"); params.append(notes)
        if image_path is not None:
            sets.append("image_path=?"); params.append(image_path)
        if rework_count is not None:
            sets.append("rework_count=?"); params.append(rework_count)
        sets.append("updated_at=?"); params.append(now)
        params += [project_id, phase, item_key]
        conn.execute(
            f"UPDATE checklist_items SET {', '.join(sets)} "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            params,
        )


def clear_checklist_image(project_id: int, phase: int, item_key: str) -> None:
    """Used at the start of a Rework cycle to force re-upload of proof."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE checklist_items SET image_path=NULL, "
            "updated_at=? "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            (datetime.utcnow().isoformat(timespec="seconds"),
             project_id, phase, item_key),
        )


def start_rework(project_id: int, phase: int, item_key: str) -> None:
    """Transition a FAILed item into REWORK: clear image, increment counter."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT rework_count FROM checklist_items "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            (project_id, phase, item_key),
        ).fetchone()
        new_count = (row["rework_count"] if row else 0) + 1
    upsert_checklist_item(
        project_id, phase, item_key,
        status=STATUS_REWORK,
        rework_count=new_count,
    )
    clear_checklist_image(project_id, phase, item_key)


def get_checklist_items(project_id: int, phase: int) -> dict[str, dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM checklist_items WHERE project_id=? AND phase_number=?",
            (project_id, phase),
        ).fetchall()
        return {r["item_key"]: dict(r) for r in rows}


# ============================ BOQ ==========================================
def set_boq_items(project_id: int, items: Iterable[dict]) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM boq_items WHERE project_id=?", (project_id,))
        conn.executemany(
            "INSERT INTO boq_items(project_id, item_name, quantity, unit, category) "
            "VALUES (?, ?, ?, ?, ?)",
            [(project_id, i["item_name"], i["quantity"], i["unit"],
              i.get("category", "structural")) for i in items],
        )


def get_boq_items(project_id: int) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM boq_items WHERE project_id=?", (project_id,)
        ).fetchall()]


def get_boq_item_by_name(project_id: int, name: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM boq_items WHERE project_id=? AND item_name=?",
            (project_id, name),
        ).fetchone()
        return dict(row) if row else None


# ============================ Blueprints ===================================
def save_blueprint(project_id: int, file_path: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO blueprints(project_id, file_path) VALUES (?, ?)",
            (project_id, file_path),
        )


def get_blueprints(project_id: int) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM blueprints WHERE project_id=?", (project_id,)
        ).fetchall()]


# ============================ Contracts ====================================
def save_contract(
    project_id: int, file_path: str, missing_clauses: str,
    risks_accepted: bool = False,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO contracts"
            "(project_id, file_path, risks_accepted, missing_clauses) "
            "VALUES (?, ?, ?, ?)",
            (project_id, file_path, int(risks_accepted), missing_clauses),
        )


def get_contract(project_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM contracts WHERE project_id=?", (project_id,)
        ).fetchone()
        return dict(row) if row else None


def update_contract_risk_acceptance(project_id: int, accepted: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE contracts SET risks_accepted=? WHERE project_id=?",
            (int(accepted), project_id),
        )


def set_contract_skipped(project_id: int, skipped: bool) -> None:
    """Mark the contract step as intentionally skipped. Creates a stub row
    if no contract has been uploaded yet so the signoff check has something
    to read."""
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT project_id FROM contracts WHERE project_id=?", (project_id,)
        ).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO contracts(project_id, file_path, "
                "risks_accepted, missing_clauses, skipped) "
                "VALUES (?, NULL, 0, '', ?)",
                (project_id, int(skipped)),
            )
        else:
            conn.execute(
                "UPDATE contracts SET skipped=? WHERE project_id=?",
                (int(skipped), project_id),
            )


# ============================ Site prep photos =============================
def save_siteprep_photo(project_id: int, kind: str, file_path: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO siteprep_photos(project_id, kind, file_path) "
            "VALUES (?, ?, ?)",
            (project_id, kind, file_path),
        )


def get_siteprep_photos(project_id: int) -> dict[str, dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM siteprep_photos WHERE project_id=?", (project_id,)
        ).fetchall()
        return {r["kind"]: dict(r) for r in rows}


# ============================ Materials ====================================
def upsert_material(
    project_id: int, phase: int, material_key: str,
    material_name: str | None = None,
    expected_qty: float | None = None,
    expected_unit: str | None = None,
    delivered_qty: float | None = None,
    invoice_path: str | None = None,
    match_status: str | None = None,
    notes: str | None = None,
) -> None:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM materials "
            "WHERE project_id=? AND phase_number=? AND material_key=?",
            (project_id, phase, material_key),
        ).fetchone()

        if existing is None:
            conn.execute(
                "INSERT INTO materials"
                "(project_id, phase_number, material_key, material_name, "
                " expected_qty, expected_unit, delivered_qty, invoice_path, "
                " match_status, notes, delivered_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    project_id, phase, material_key, material_name,
                    expected_qty, expected_unit,
                    delivered_qty, invoice_path,
                    match_status or MATCH_PENDING,
                    notes or "",
                    now if invoice_path else None,
                ),
            )
            return

        sets, params = [], []
        for col, val in [
            ("material_name", material_name),
            ("expected_qty", expected_qty),
            ("expected_unit", expected_unit),
            ("delivered_qty", delivered_qty),
            ("invoice_path", invoice_path),
            ("match_status", match_status),
            ("notes", notes),
        ]:
            if val is not None:
                sets.append(f"{col}=?"); params.append(val)
        if invoice_path is not None:
            sets.append("delivered_at=?"); params.append(now)
        if not sets:
            return
        params += [project_id, phase, material_key]
        conn.execute(
            f"UPDATE materials SET {', '.join(sets)} "
            "WHERE project_id=? AND phase_number=? AND material_key=?",
            params,
        )


def get_materials(project_id: int, phase: int) -> dict[str, dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM materials WHERE project_id=? AND phase_number=?",
            (project_id, phase),
        ).fetchall()
        return {r["material_key"]: dict(r) for r in rows}


# ============================ Financials ===================================
def add_financial(
    project_id: int, phase: int, milestone_name: str, percentage: float
) -> None:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM financials "
            "WHERE project_id=? AND phase_number=? AND milestone_name=?",
            (project_id, phase, milestone_name),
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO financials"
                "(project_id, phase_number, milestone_name, percentage) "
                "VALUES (?, ?, ?, ?)",
                (project_id, phase, milestone_name, percentage),
            )


def mark_payment_released(
    project_id: int, phase: int, milestone_name: str
) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE financials SET paid=1, paid_at=? "
            "WHERE project_id=? AND phase_number=? AND milestone_name=?",
            (datetime.utcnow().isoformat(timespec="seconds"),
             project_id, phase, milestone_name),
        )


def get_financials(project_id: int) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM financials WHERE project_id=? ORDER BY phase_number",
            (project_id,),
        ).fetchall()]


# ============================ Payment certificates ========================
def save_payment_certificate(
    project_id: int, phase: int, certificate_no: str,
    percentage: float, amount: float, file_path: str,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO payment_certificates"
            "(project_id, phase_number, certificate_no, percentage, amount, file_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, phase, certificate_no, percentage, amount, file_path),
        )


def get_payment_certificates(project_id: int) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM payment_certificates WHERE project_id=? "
            "ORDER BY phase_number, issued_at",
            (project_id,),
        ).fetchall()]


# ============================ Timers =======================================
def add_timer(
    project_id: int, phase: int, timer_key: str,
    label: str, duration_seconds: int,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO timers"
            "(project_id, phase_number, timer_key, label, duration_seconds) "
            "VALUES (?, ?, ?, ?, ?)",
            (project_id, phase, timer_key, label, duration_seconds),
        )


def get_timers(project_id: int) -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM timers WHERE project_id=?", (project_id,)
        ).fetchall()]
