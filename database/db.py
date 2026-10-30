"""
SQLite database initialization and connection management.
"""

import sqlite3
import os
from pathlib import Path
from config import DB_PATH

def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Get a configured SQLite connection with foreign keys enabled and row factory set.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DB_PATH) -> None:
    """
    Idempotent schema initialization with appropriate tables, foreign keys, and indexes.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    # 1. Documents & Source Metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        source_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        sha256_hash TEXT NOT NULL UNIQUE,
        source_type TEXT NOT NULL,
        source_url TEXT,
        captured_at TEXT NOT NULL,
        detected_language TEXT NOT NULL,
        total_pages INTEGER NOT NULL,
        has_scanned_pages INTEGER NOT NULL,
        ocr_method TEXT,
        warnings TEXT, -- JSON array
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Document Pages (stores raw page text and OCR diagnostics)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS document_pages (
        page_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT NOT NULL,
        page_number INTEGER NOT NULL,
        text_content TEXT NOT NULL,
        is_scanned INTEGER NOT NULL DEFAULT 0,
        ocr_applied INTEGER NOT NULL DEFAULT 0,
        character_count INTEGER NOT NULL,
        FOREIGN KEY (source_id) REFERENCES documents (source_id) ON DELETE CASCADE,
        UNIQUE (source_id, page_number)
    );
    """)

    # 3. Extraction Runs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS extraction_runs (
        run_id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        scheme_ref TEXT NOT NULL,
        model_name TEXT NOT NULL,
        model_version TEXT NOT NULL,
        provider TEXT NOT NULL,
        prompt_version TEXT NOT NULL,
        input_tokens INTEGER DEFAULT 0,
        output_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        estimated_cost_usd REAL,
        cost_status TEXT NOT NULL,
        latency_seconds REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES documents (source_id) ON DELETE CASCADE
    );
    """)

    # 4. Schemes
    cur.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        scheme_ref TEXT PRIMARY KEY,
        scheme_name TEXT NOT NULL,
        source_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        approval_status TEXT NOT NULL DEFAULT 'pending_review',
        approval_notes TEXT,
        approved_by TEXT,
        approved_at TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES documents (source_id) ON DELETE CASCADE,
        FOREIGN KEY (run_id) REFERENCES extraction_runs (run_id) ON DELETE CASCADE
    );
    """)

    # 5. Field Records & Evidence
    cur.execute("""
    CREATE TABLE IF NOT EXISTS field_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_ref TEXT NOT NULL,
        field TEXT NOT NULL,
        value TEXT,
        confidence REAL NOT NULL,
        status TEXT NOT NULL,
        note TEXT,
        evidence_text TEXT,
        evidence_page INTEGER,
        evidence_section TEXT,
        evidence_source TEXT,
        evidence_source_id TEXT,
        evidence_captured_at TEXT,
        evidence_source_url TEXT,
        evidence_verified INTEGER NOT NULL DEFAULT 0,
        evidence_verification_score REAL DEFAULT 0.0,
        evidence_verification_note TEXT,
        structured_benefit TEXT, -- JSON
        reviewer_value TEXT,
        reviewer_accepted INTEGER,
        reviewer_notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scheme_ref) REFERENCES schemes (scheme_ref) ON DELETE CASCADE,
        UNIQUE (scheme_ref, field)
    );
    """)

    # 6. Conflict Groups
    cur.execute("""
    CREATE TABLE IF NOT EXISTS conflict_groups (
        conflict_id TEXT PRIMARY KEY,
        scheme_ref TEXT NOT NULL,
        field TEXT NOT NULL,
        records_json TEXT NOT NULL, -- JSON array of conflicting source items
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved INTEGER NOT NULL DEFAULT 0,
        resolution_choice TEXT,
        resolution_reason TEXT,
        resolved_by TEXT,
        resolved_at TEXT,
        FOREIGN KEY (scheme_ref) REFERENCES schemes (scheme_ref) ON DELETE CASCADE
    );
    """)

    # 7. Evaluation Runs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evaluation_runs (
        eval_id TEXT PRIMARY KEY,
        run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        overall_accuracy REAL,
        overall_precision REAL,
        overall_recall REAL,
        overall_f1 REAL,
        evidence_validity_rate REAL,
        conflict_detection_recall REAL,
        results_json TEXT NOT NULL
    );
    """)

    # Indexes for fast lookup
    cur.execute("CREATE INDEX IF NOT EXISTS idx_doc_pages_source ON document_pages(source_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_field_records_scheme ON field_records(scheme_ref);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_conflicts_scheme ON conflict_groups(scheme_ref);")

    conn.commit()
    conn.close()

# Initialize upon import if not present
init_db()
