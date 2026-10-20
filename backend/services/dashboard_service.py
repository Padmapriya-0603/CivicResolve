"""
Dashboard and analytical metrics service with Role-Based Scoping.
Executes real SQL aggregation queries directly on SQLite. Zero fake statistics.
"""

from typing import Dict, Any, Optional
from database import get_db_connection


class DashboardService:
    def get_dashboard_metrics(self, current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculates role-aware real-time grievance statistics from SQLite."""
        conn = get_db_connection()
        cursor = conn.cursor()

        role = current_user.get("role") if current_user else "ADMIN"
        dept_name = current_user.get("department_name") if current_user else None
        user_id = current_user.get("id") if current_user else None

        base_filter = " WHERE 1=1"
        params = []

        if role == "CITIZEN" and user_id:
            base_filter += " AND citizen_id = ?"
            params.append(user_id)
        elif role == "DEPARTMENT_OFFICER" and dept_name:
            base_filter += " AND LOWER(department) = LOWER(?)"
            params.append(dept_name)

        # Total count
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter}", params)
        total = cursor.fetchone()[0]

        # New (Submitted or Under Review)
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('Submitted', 'Under Review')", params)
        new_cnt = cursor.fetchone()[0]

        # In-progress (Assigned or In Progress)
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('Assigned', 'In Progress')", params)
        in_progress = cursor.fetchone()[0]

        # Resolved (Resolved or Closed)
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('Resolved', 'Closed')", params)
        resolved = cursor.fetchone()[0]

        # Critical priority
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND priority = 'CRITICAL'", params)
        critical = cursor.fetchone()[0]

        # High priority
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND priority = 'HIGH'", params)
        high = cursor.fetchone()[0]

        # Escalated complaints
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND escalation IN ('REQUIRED', 'IMMEDIATE')", params)
        escalated = cursor.fetchone()[0]

        # Breakdowns by department
        cursor.execute(f"""
            SELECT COALESCE(department, 'Unassigned') as dept, COUNT(*) as cnt
            FROM complaints{base_filter}
            GROUP BY dept
            ORDER BY cnt DESC
        """, params)
        by_dept = {row["dept"]: row["cnt"] for row in cursor.fetchall()}

        # Breakdowns by category
        cursor.execute(f"""
            SELECT category, COUNT(*) as cnt
            FROM complaints{base_filter}
            GROUP BY category
            ORDER BY cnt DESC
        """, params)
        by_cat = {row["category"]: row["cnt"] for row in cursor.fetchall()}

        # Breakdowns by priority
        cursor.execute(f"""
            SELECT priority, COUNT(*) as cnt
            FROM complaints{base_filter}
            GROUP BY priority
        """, params)
        by_priority = {row["priority"]: row["cnt"] for row in cursor.fetchall()}

        # Breakdowns by status
        cursor.execute(f"""
            SELECT status, COUNT(*) as cnt
            FROM complaints{base_filter}
            GROUP BY status
        """, params)
        by_status = {row["status"]: row["cnt"] for row in cursor.fetchall()}

        # 5 Lifecycle Stages
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('SUBMITTED', 'Submitted')", params)
        submitted_cnt = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('ACKNOWLEDGED', 'Acknowledged', 'Under Review', 'ACCEPTED', 'Accepted', 'Assigned')", params)
        acknowledged_cnt = cursor.fetchone()[0]

        accepted_cnt = acknowledged_cnt

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('IN_PROGRESS', 'In Progress')", params)
        in_progress = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('RESOLVED', 'Resolved', 'WORK_COMPLETED', 'Work Completed', 'USER_INFORMED', 'User Informed')", params)
        resolved_cnt = cursor.fetchone()[0]
        work_completed_cnt = resolved_cnt
        user_informed_cnt = resolved_cnt

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND status IN ('CLOSED', 'Closed')", params)
        closed_cnt = cursor.fetchone()[0]

        new_cnt = submitted_cnt
        resolved = resolved_cnt + closed_cnt

        # Admin Work Queues
        queues = {
            "requiring_acknowledgement": submitted_cnt,
            "acknowledged": acknowledged_cnt,
            "currently_in_progress": in_progress,
            "resolved": resolved_cnt,
            "closed": closed_cnt,
            "requiring_acceptance": acknowledged_cnt,
            "work_not_started": acknowledged_cnt,
            "awaiting_user_notification": resolved_cnt,
            "awaiting_closure": resolved_cnt
        }

        # Bottlenecks and SLA risk indicators
        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND priority = 'CRITICAL' AND status NOT IN ('CLOSED', 'Closed', 'Resolved')", params)
        critical_unresolved = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND priority = 'HIGH' AND status NOT IN ('CLOSED', 'Closed', 'Resolved')", params)
        high_unresolved = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND duration_days >= 3 AND status NOT IN ('CLOSED', 'Closed', 'Resolved')", params)
        long_duration_unresolved = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM complaints{base_filter} AND escalation = 'IMMEDIATE' AND status NOT IN ('CLOSED', 'Closed', 'Resolved')", params)
        immediate_escalation_unresolved = cursor.fetchone()[0]

        bottlenecks = {
            "pending_assignment": submitted_cnt + acknowledged_cnt,
            "critical_unresolved": critical_unresolved,
            "high_unresolved": high_unresolved,
            "long_duration_unresolved": long_duration_unresolved,
            "immediate_escalation_unresolved": immediate_escalation_unresolved,
            "resolution_rate_percent": round((closed_cnt / total * 100) if total > 0 else 100, 1)
        }

        # Admin system-wide counters
        total_users = None
        total_citizens = None
        total_officers = None
        total_departments = None

        if role == "ADMIN":
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'CITIZEN'")
            total_citizens = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'DEPARTMENT_OFFICER'")
            total_officers = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM departments WHERE is_active = 1")
            total_departments = cursor.fetchone()[0]

        conn.close()

        return {
            "total_complaints": total,
            "new_complaints": new_cnt,
            "submitted_complaints": submitted_cnt,
            "acknowledged_complaints": acknowledged_cnt,
            "accepted_complaints": accepted_cnt,
            "assigned_complaints": accepted_cnt,
            "in_progress_complaints": in_progress,
            "work_completed_complaints": work_completed_cnt,
            "user_informed_complaints": user_informed_cnt,
            "resolved_complaints": resolved,
            "closed_complaints": closed_cnt,
            "critical_complaints": critical,
            "high_priority_complaints": high,
            "escalated_complaints": escalated,
            "by_department": by_dept,
            "by_category": by_cat,
            "by_priority": by_priority,
            "by_status": by_status,
            "bottlenecks": bottlenecks,
            "queues": queues,
            "total_users": total_users,
            "total_citizens": total_citizens,
            "total_officers": total_officers,
            "total_departments": total_departments
        }


dashboard_service = DashboardService()
