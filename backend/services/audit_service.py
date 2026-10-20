"""
Audit Logging service for Public Grievance AI (Section 57).
Records immutable administrative and lifecycle operations:
- Login / Logout
- Complaint creation
- Status updates
- Department overrides
- Rule changes & activations
- User role changes & activations
"""

from typing import Optional, List, Dict, Any
from database import get_db_connection


class AuditService:
    @staticmethod
    def log_event(
        action: str,
        entity_type: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        reason: Optional[str] = None
    ) -> None:
        """Persists a new structured audit log record."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (
                    user_id, user_email, action, entity_type, entity_id, old_value, new_value, reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_email,
                action,
                entity_type,
                str(entity_id) if entity_id is not None else None,
                old_value,
                new_value,
                reason
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[AUDIT LOGGING ERROR] Failed to record audit log: {e}")

    @staticmethod
    def get_audit_logs(limit: int = 200) -> List[Dict[str, Any]]:
        """Retrieves system audit records for administrators, ordered newest first."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, user_email, action, entity_type, entity_id, old_value, new_value, reason, timestamp
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        logs = [dict(r) for r in rows]
        conn.close()
        return logs


audit_service = AuditService()
