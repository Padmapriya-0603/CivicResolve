"""
Database management and SQLite connection lifecycle for Public Grievance AI.
Provides table creation, connection helper, row factory initialization,
and migration helpers for RBAC and audit logs.
"""

import sqlite3
import os
from pathlib import Path

# SQLite database file path
BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "grievances.db"


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection configured with Row factory and FK enforcement."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initializes the database schema if tables do not already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Departments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        supported_issues TEXT NOT NULL, -- JSON array of issue types
        escalation_authority TEXT NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Categories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL
    );
    """)

    # 3. Issue Types table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issue_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        issue_type_id TEXT UNIQUE NOT NULL,
        category_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        default_department_id TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
    );
    """)

    # 4. Rules table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id TEXT UNIQUE NOT NULL,
        rule_name TEXT NOT NULL,
        rule_type TEXT NOT NULL, -- ROUTING, PRIORITY, ESCALATION, CONFLICT
        description TEXT NOT NULL,
        conditions_json TEXT NOT NULL, -- JSON representation of conditions
        conclusion_json TEXT NOT NULL, -- JSON representation of conclusion
        priority_order INTEGER NOT NULL DEFAULT 10,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Users table for RBAC (Section 45)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('CITIZEN', 'DEPARTMENT_OFFICER', 'ADMIN')),
        department_id TEXT, -- NULL for citizens and admins, identifies department for officers
        is_active BOOLEAN NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (department_id)
    );
    """)

    # 6. Complaints table (with citizen_id and admin override tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        citizen_id INTEGER, -- FK to users(id)
        citizen_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        zone TEXT,
        ward TEXT NOT NULL,
        location TEXT NOT NULL,
        preferred_contact TEXT NOT NULL,
        category TEXT NOT NULL,
        issue_type TEXT NOT NULL,
        duration_days INTEGER,
        severity TEXT NOT NULL,
        affected_people INTEGER,
        frequency TEXT NOT NULL,
        evidence_available BOOLEAN NOT NULL DEFAULT 0,
        evidence_filename TEXT,
        safety_risk TEXT NOT NULL,
        public_accessibility_affected BOOLEAN NOT NULL DEFAULT 0,
        recurrence BOOLEAN NOT NULL DEFAULT 0,
        emergency BOOLEAN NOT NULL DEFAULT 0,
        
        -- Routing and AI Reasoning outcomes
        department TEXT,
        ai_department TEXT,
        manual_override BOOLEAN NOT NULL DEFAULT 0,
        manual_department TEXT,
        manual_override_reason TEXT,
        overridden_by TEXT,
        override_timestamp TIMESTAMP,
        priority TEXT NOT NULL,
        escalation TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Submitted',
        
        -- Auditable structured reasoning info
        missing_info_json TEXT, -- JSON array of missing evaluations
        conflicts_json TEXT,    -- JSON array of detected conflicts
        explanation TEXT,
        
        admin_message TEXT,     -- Message/description sent by Administrator to citizen upon acceptance
        resolution_message TEXT,-- Message sent to citizen upon task completion
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (citizen_id) REFERENCES users (id) ON DELETE SET NULL
    );
    """)

    # Column migrations if database already existed
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN zone TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN admin_message TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE complaints ADD COLUMN resolution_message TEXT")
    except Exception:
        pass

    # 7. Reasoning traces table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reasoning_traces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        step_type TEXT NOT NULL, -- INPUT_FACT, RULE_MATCH, DERIVED_FACT, CONFLICT_RESOLUTION, ESCALATION, FINAL_DECISION
        rule_id TEXT,
        rule_name TEXT,
        conditions_evaluated_json TEXT,
        derived_fact_json TEXT,
        explanation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
    );
    """)

    # 8. Status history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        previous_status TEXT,
        new_status TEXT NOT NULL,
        changed_by TEXT NOT NULL DEFAULT 'SYSTEM',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
    );
    """)

    # 9. Audit Logs table (Section 57)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_email TEXT,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        old_value TEXT,
        new_value TEXT,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    );
    """)

    # 10. Complaint Timeline table (Section 88)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_timeline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT NOT NULL,
        message_type TEXT NOT NULL DEFAULT 'SYSTEM', -- ACKNOWLEDGEMENT, ACCEPTANCE, PROGRESS_UPDATE, COMPLETION, CLOSURE, SYSTEM
        action_by TEXT NOT NULL,
        action_by_role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
    );
    """)

    # 11. In-App Notifications table (Section 89)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        complaint_id TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT NOT NULL,
        is_read BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
    );
    """)

    # 12. Complaint Messages table (Section 33)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT NOT NULL,
        admin_id INTEGER,
        message TEXT NOT NULL,
        message_type TEXT NOT NULL, -- ACKNOWLEDGEMENT, ACCEPTANCE, PROGRESS_UPDATE, COMPLETION, FINAL_RESPONSE, CLOSURE
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE,
        FOREIGN KEY (admin_id) REFERENCES users (id) ON DELETE SET NULL
    );
    """)

    # 13. Complaint Reasoning History table (Section 37)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint_reasoning (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        input_facts TEXT NOT NULL,          -- JSON of input facts
        constraints_checked TEXT NOT NULL,  -- JSON list of CSP constraint checks
        CSP_result TEXT NOT NULL,           -- JSON string or boolean of CSP validation
        rules_evaluated TEXT NOT NULL,      -- JSON list of evaluated rules
        rules_fired TEXT NOT NULL,          -- JSON list of fired rules
        derived_facts TEXT NOT NULL,        -- JSON of derived facts
        final_conclusions TEXT NOT NULL,    -- JSON of final determinations
        explanation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (complaint_id) REFERENCES complaints (complaint_id) ON DELETE CASCADE
    );
    """)

    # 14. Password Resets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        reset_code TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used BOOLEAN NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Check and add columns to complaints if migrating existing db
    cursor.execute("PRAGMA table_info(complaints)")
    cols = [col[1] for col in cursor.fetchall()]
    new_cols = [
        ("citizen_id", "INTEGER REFERENCES users(id)"),
        ("complaint_number", "TEXT"),
        ("location_type", "TEXT DEFAULT 'Public Road'"),
        ("immediate_danger", "TEXT DEFAULT 'NO'"),
        ("description", "TEXT"),
        ("ai_priority", "TEXT"),
        ("final_priority", "TEXT"),
        ("ai_escalation", "TEXT"),
        ("final_escalation", "TEXT"),
        ("ai_department_id", "TEXT"),
        ("admin_department_id", "TEXT"),
        ("manual_department", "TEXT"),
        ("overridden_by", "TEXT"),
        ("override_timestamp", "TIMESTAMP"),
        ("admin_message", "TEXT"),
        ("resolution_message", "TEXT"),
        ("work_started_message", "TEXT"),
        ("completion_message", "TEXT"),
        ("completed_by", "TEXT"),
        ("completed_at", "TIMESTAMP"),
        ("notification_message", "TEXT"),
        ("informed_by", "TEXT"),
        ("informed_at", "TIMESTAMP"),
        ("closure_message", "TEXT"),
        ("closed_by", "TEXT"),
        ("closed_at", "TIMESTAMP")
    ]
    for col_name, col_type in new_cols:
        if col_name not in cols:
            try:
                cursor.execute(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_FILE)
