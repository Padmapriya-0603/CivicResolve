"""
Seed Data Script for Public Grievance AI.
Populates SQLite with departments, categories, issue taxonomies, production rules,
and the requested citizen and administrator accounts.
Leaves complaints empty (zero filled complaints).
"""

import json
from datetime import datetime
from database import get_db_connection, init_db
from ai.knowledge_base import DEPARTMENTS_KB
from utils.validators import CATEGORY_ISSUE_MAP
from ai.rules import get_default_rules
from utils.security import hash_password


def seed_database(clean_complaints: bool = True):
    """Initializes tables and seeds knowledge entities and clean accounts."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Seed Departments
    for dept in DEPARTMENTS_KB:
        cursor.execute("""
            INSERT OR REPLACE INTO departments (
                department_id, name, description, supported_issues, escalation_authority, is_active
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            dept["department_id"],
            dept["name"],
            dept["description"],
            json.dumps(dept["supported_issues"]),
            dept["escalation_authority"],
            1 if dept.get("is_active", True) else 0
        ))

    # 2. Seed Categories and Issue Types
    for cat_name, issue_list in CATEGORY_ISSUE_MAP.items():
        cat_id = f"CAT_{cat_name.upper().replace(' ', '_')}"
        cursor.execute("""
            INSERT OR REPLACE INTO categories (category_id, name, description)
            VALUES (?, ?, ?)
        """, (
            cat_id,
            cat_name,
            f"Public grievance category concerning municipal {cat_name.lower()}."
        ))

        # Seed Issue Types
        for issue_name in issue_list:
            issue_id = f"ISSUE_{issue_name.upper().replace(' ', '_')}"
            cursor.execute("""
                INSERT OR REPLACE INTO issue_types (issue_type_id, category_id, name, description, default_department_id)
                VALUES (?, ?, ?, ?, ?)
            """, (
                issue_id,
                cat_id,
                issue_name,
                f"Citizen-reported issue regarding {issue_name.lower()}.",
                "DEPT_CIVIC_ADMIN"
            ))

    # 3. Seed Production Rules
    rules = get_default_rules()
    for rule in rules:
        conds_serialized = [
            {"field": c.field, "operator": c.operator, "value": c.value}
            for c in rule.conditions
        ]
        cursor.execute("""
            INSERT OR REPLACE INTO rules (
                rule_id, rule_name, rule_type, description, conditions_json, conclusion_json, priority_order, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rule.rule_id,
            rule.rule_name,
            rule.rule_type,
            rule.description,
            json.dumps(conds_serialized),
            json.dumps(rule.conclusion),
            rule.priority_order,
            1 if rule.is_active else 0
        ))

    # 4. Clean Complaints and Child Tables FIRST to satisfy Foreign Keys
    if clean_complaints:
        cursor.execute("DELETE FROM complaint_reasoning")
        cursor.execute("DELETE FROM reasoning_traces")
        cursor.execute("DELETE FROM status_history")
        cursor.execute("DELETE FROM complaint_timeline")
        cursor.execute("DELETE FROM complaint_messages")
        cursor.execute("DELETE FROM notifications")
        cursor.execute("DELETE FROM audit_logs")
        cursor.execute("DELETE FROM complaints")

    # 5. Remove Old Demo Accounts
    demo_emails = [
        "citizen@grievance.local",
        "priya@grievance.local",
        "lighting@grievance.local",
        "water@grievance.local",
        "roads@grievance.local",
        "inactive@grievance.local",
        "new_officer_test@grievance.local",
    ]
    cursor.execute(
        f"DELETE FROM users WHERE email IN ({','.join(['?'] * len(demo_emails))}) OR email LIKE 'officer_%@grievance.local'",
        demo_emails,
    )

    # 6. Seed Citizen Account: Priya (priya@gmail.com / 123456)
    cursor.execute("SELECT id FROM users WHERE email = 'priya@gmail.com'")
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE users SET name = 'priya', phone = '+91 98765 12345',
            password_hash = ?, role = 'CITIZEN', department_id = NULL, is_active = 1
            WHERE email = 'priya@gmail.com'
        """, (hash_password("123456"),))
    else:
        cursor.execute("""
            INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
            VALUES ('priya', 'priya@gmail.com', '+91 98765 12345', ?, 'CITIZEN', NULL, 1)
        """, (hash_password("123456"),))

    # 7. Seed Admin Account (admin@gmail.com / 123456)
    cursor.execute("SELECT id FROM users WHERE email = 'admin@gmail.com'")
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE users SET name = 'Administrator', phone = '+91 99000 11000',
            password_hash = ?, role = 'ADMIN', department_id = NULL, is_active = 1
            WHERE email = 'admin@gmail.com'
        """, (hash_password("123456"),))
    else:
        cursor.execute("""
            INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
            VALUES ('Administrator', 'admin@gmail.com', '+91 99000 11000', ?, 'ADMIN', NULL, 1)
        """, (hash_password("123456"),))

    # Also maintain admin@grievance.local with password 123456 for convenience
    cursor.execute("SELECT id FROM users WHERE email = 'admin@grievance.local'")
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE users SET name = 'Administrator', phone = '+91 99000 11000',
            password_hash = ?, role = 'ADMIN', department_id = NULL, is_active = 1
            WHERE email = 'admin@grievance.local'
        """, (hash_password("123456"),))
    else:
        cursor.execute("""
            INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
            VALUES ('Administrator', 'admin@grievance.local', '+91 99000 11000', ?, 'ADMIN', NULL, 1)
        """, (hash_password("123456"),))

    # 8. Seed 5 Department Officers (Road Maintenance, Water Supply, Sanitation, Public Lighting, Drainage)
    officers = [
        {
            "name": "Officer Rajesh (Roads)",
            "email": "officer.roads@gmail.com",
            "phone": "+91 98888 22001",
            "dept_id": "DEPT_ROAD_MAINT",
            "alias_email": "officer@gmail.com"
        },
        {
            "name": "Officer Suresh (Water)",
            "email": "officer.water@gmail.com",
            "phone": "+91 98888 22002",
            "dept_id": "DEPT_WATER_SUPPLY",
            "alias_email": None
        },
        {
            "name": "Officer Ramesh (Sanitation)",
            "email": "officer.sanitation@gmail.com",
            "phone": "+91 98888 22003",
            "dept_id": "DEPT_SANITATION",
            "alias_email": None
        },
        {
            "name": "Officer Anitha (Lighting)",
            "email": "officer.lighting@gmail.com",
            "phone": "+91 98888 22004",
            "dept_id": "DEPT_PUB_LIGHTING",
            "alias_email": None
        },
        {
            "name": "Officer Vikram (Drainage)",
            "email": "officer.drainage@gmail.com",
            "phone": "+91 98888 22005",
            "dept_id": "DEPT_DRAINAGE",
            "alias_email": None
        },
    ]

    pw_hash = hash_password("123456")
    for off in officers:
        cursor.execute("SELECT id FROM users WHERE email = ?", (off["email"],))
        exist = cursor.fetchone()
        if exist:
            cursor.execute("""
                UPDATE users SET name = ?, phone = ?, password_hash = ?, role = 'DEPARTMENT_OFFICER', department_id = ?, is_active = 1
                WHERE email = ?
            """, (off["name"], off["phone"], pw_hash, off["dept_id"], off["email"]))
        else:
            cursor.execute("""
                INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
                VALUES (?, ?, ?, ?, 'DEPARTMENT_OFFICER', ?, 1)
            """, (off["name"], off["email"], off["phone"], pw_hash, off["dept_id"]))

        if off["alias_email"]:
            cursor.execute("SELECT id FROM users WHERE email = ?", (off["alias_email"],))
            exist_alias = cursor.fetchone()
            if exist_alias:
                cursor.execute("""
                    UPDATE users SET name = ?, phone = ?, password_hash = ?, role = 'DEPARTMENT_OFFICER', department_id = ?, is_active = 1
                    WHERE email = ?
                """, (off["name"], off["phone"], pw_hash, off["dept_id"], off["alias_email"]))
            else:
                cursor.execute("""
                    INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
                    VALUES (?, ?, ?, ?, 'DEPARTMENT_OFFICER', ?, 1)
                """, (off["name"], off["alias_email"], off["phone"], pw_hash, off["dept_id"]))

    conn.commit()
    conn.close()
    print("Database seeded: Departments, taxonomy, rules, and requested user accounts created.")
    if clean_complaints:
        print("Complaints registry cleared: 0 complaints.")


if __name__ == "__main__":
    seed_database(clean_complaints=True)
