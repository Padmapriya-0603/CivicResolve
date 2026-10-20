"""
Service layer orchestrating grievance transactions, reasoning engine execution,
audit trace persistence, manual department overrides, complete 5-stage lifecycle state machine,
complaint timeline history, in-app notifications, and RBAC resource scoping.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import get_db_connection
from models.schemas import ComplaintCreateRequest, ConflictDetail
from utils.validators import validate_complaint_constraints
from ai.csp_solver import csp_solver
from ai.grievance_agent import GrievanceAgent
from services.audit_service import audit_service


# 5-Stage Grievance Lifecycle Progression
STAGE_PROGRESS = {
    "SUBMITTED": (1, 20, "Complaint Submitted"),
    "ACKNOWLEDGED": (2, 40, "Complaint Acknowledged"),
    "ACCEPTED": (2, 40, "Complaint Acknowledged"),
    "IN_PROGRESS": (3, 60, "Work in Progress"),
    "RESOLVED": (4, 80, "Complaint Resolved"),
    "WORK_COMPLETED": (4, 80, "Complaint Resolved"),
    "USER_INFORMED": (4, 80, "Complaint Resolved"),
    "CLOSED": (5, 100, "Complaint Closed"),
}

LEGACY_STATUS_MAP = {
    "Submitted": "SUBMITTED",
    "Under Review": "ACKNOWLEDGED",
    "Assigned": "ACKNOWLEDGED",
    "Accepted": "ACKNOWLEDGED",
    "ACCEPTED": "ACKNOWLEDGED",
    "In Progress": "IN_PROGRESS",
    "Work Completed": "RESOLVED",
    "WORK_COMPLETED": "RESOLVED",
    "User Informed": "RESOLVED",
    "USER_INFORMED": "RESOLVED",
    "Resolved": "RESOLVED",
    "Closed": "CLOSED",
    "CLOSED": "CLOSED"
}

ALLOWED_TRANSITIONS = {
    "SUBMITTED": ["ACKNOWLEDGED", "ACCEPTED"],
    "ACKNOWLEDGED": ["ACCEPTED", "IN_PROGRESS"],
    "ACCEPTED": ["IN_PROGRESS"],
    "IN_PROGRESS": ["RESOLVED", "WORK_COMPLETED", "IN_PROGRESS"],
    "WORK_COMPLETED": ["RESOLVED", "USER_INFORMED", "CLOSED"],
    "USER_INFORMED": ["RESOLVED", "CLOSED"],
    "RESOLVED": ["CLOSED"],
    "CLOSED": []
}


def normalize_status(st: Optional[str]) -> str:
    if not st:
        return "SUBMITTED"
    upper = st.upper().replace(" ", "_")
    if upper in STAGE_PROGRESS:
        return upper
    if st in LEGACY_STATUS_MAP:
        return LEGACY_STATUS_MAP[st]
    return upper


def add_timeline_entry(
    conn,
    complaint_id: str,
    status: str,
    message: str,
    action_by: str,
    action_by_role: str,
    message_type: str = "SYSTEM"
):
    """Appends an immutable event to complaint_timeline (Section 88)."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaint_timeline (
            complaint_id, status, message, message_type, action_by, action_by_role
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (complaint_id, status, message, message_type, action_by, action_by_role))


def add_complaint_message(
    conn,
    complaint_id: str,
    admin_id: Optional[int],
    message: str,
    message_type: str
):
    """Appends an admin communication event to complaint_messages (Section 33)."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO complaint_messages (complaint_id, admin_id, message, message_type)
        VALUES (?, ?, ?, ?)
    """, (complaint_id, admin_id, message, message_type))


def add_notification(
    conn,
    user_id: Optional[int],
    complaint_id: str,
    title: str,
    message: str,
    n_type: str
):
    """Creates an in-app notification for the citizen (Section 89)."""
    if not user_id:
        return
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (user_id, complaint_id, title, message, type, is_read)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (user_id, complaint_id, title, message, n_type))


class ComplaintService:
    def __init__(self):
        self.agent = GrievanceAgent()

    def create_complaint(self, req: ComplaintCreateRequest, citizen_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes constraint checking, AI grievance agent reasoning,
        atomic SQLite persistence, initial SUBMITTED timeline record,
        and citizen notification.
        """
        # 1. Constraint Satisfaction Problem Validation (Sections 8, 9, 10)
        req_dict = req.model_dump()
        csp_res = csp_solver.validate_and_solve(req_dict)
        if not csp_res.is_valid:
            raise ValueError(f"Constraint Satisfaction Failure: {' | '.join(csp_res.violations)}")

        # 2. Grievance Agent Processing (Forward Chaining + Rule Deduction)
        reasoning_res = self.agent.process_grievance(req)
        if not reasoning_res.get("success", False):
            raise ValueError(reasoning_res.get("error", "Reasoning processing failed."))

        dept = reasoning_res.get("department") or csp_res.inferred_department or "General Civic Administration"
        priority = reasoning_res.get("priority", "LOW")
        escalation = reasoning_res.get("escalation", "NO_ESCALATION")
        conflicts = reasoning_res.get("conflicts", [])
        missing_info = reasoning_res.get("missing_info", [])
        trace = reasoning_res.get("reasoning_trace", [])
        explanation = reasoning_res.get("explanation", "") or csp_res.explanation

        conn = get_db_connection()
        cursor = conn.cursor()

        # 3. Generate Complaint ID & Complaint Number (Section 16)
        now = datetime.now()
        prefix = f"GRV-{now.strftime('%Y%m')}-"
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE complaint_id LIKE ?", (f"{prefix}%",))
        seq = cursor.fetchone()[0] + 1
        complaint_id = f"{prefix}{str(seq).zfill(4)}"

        # 4. Insert into complaints with initial status SUBMITTED (Section 15)
        imm_danger = req.immediate_danger or ("YES" if req.emergency else "NO")
        loc_type = req.location_type or "Public Road"
        cursor.execute("""
            INSERT INTO complaints (
                complaint_id, complaint_number, citizen_id, citizen_name, phone, email, zone, ward, location,
                location_type, preferred_contact, category, issue_type, duration_days, severity,
                immediate_danger, affected_people, description, frequency, evidence_available,
                evidence_filename, safety_risk, public_accessibility_affected, recurrence,
                emergency, department, ai_department, manual_override, manual_department,
                manual_override_reason, overridden_by, override_timestamp, priority, ai_priority,
                final_priority, escalation, ai_escalation, final_escalation, status,
                missing_info_json, conflicts_json, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_id, complaint_id, citizen_id, req.citizen_name, req.phone, req.email, req.zone, req.ward, req.location,
            loc_type, req.preferred_contact, req.category, req.issue_type, req.duration_days, req.severity,
            imm_danger, req.affected_people, req.description, req.frequency,
            1 if req.evidence_available else 0, req.evidence_filename, req.safety_risk,
            1 if req.public_accessibility_affected else 0, 1 if req.recurrence else 0,
            1 if req.emergency else 0, dept, dept, 0, None, None, None, None,
            priority, priority, priority, escalation, escalation, escalation, "SUBMITTED",
            json.dumps(missing_info), json.dumps(conflicts), explanation
        ))

        # 5. Insert into complaint_reasoning (Section 37)
        cursor.execute("""
            INSERT OR REPLACE INTO complaint_reasoning (
                complaint_id, input_facts, constraints_checked, CSP_result,
                rules_evaluated, rules_fired, derived_facts, final_conclusions, explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint_id,
            json.dumps(csp_res.assigned_variables),
            json.dumps([c.model_dump() for c in csp_res.constraints_checked]),
            json.dumps({"is_valid": csp_res.is_valid, "violations": csp_res.violations, "warnings": csp_res.warnings}),
            json.dumps([r.rule_id for r in self.agent.rules]),
            json.dumps([s["rule_id"] for s in trace if s.get("rule_id")]),
            json.dumps({"priority": priority, "escalation": escalation, "department": dept}),
            json.dumps({"department": dept, "priority": priority, "escalation": escalation}),
            explanation
        ))

        # 6. Insert Reasoning Trace Steps
        for step in trace:
            cursor.execute("""
                INSERT INTO reasoning_traces (
                    complaint_id, step_order, step_type, rule_id, rule_name,
                    conditions_evaluated_json, derived_fact_json, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                complaint_id,
                step["step_order"],
                step["step_type"],
                step.get("rule_id"),
                step.get("rule_name"),
                json.dumps(step.get("conditions_evaluated", {})),
                json.dumps(step.get("derived_fact", {})),
                step.get("explanation", "")
            ))

        # 6. Status History Record
        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            complaint_id,
            None,
            "SUBMITTED",
            req.citizen_name or "Citizen",
            "Grievance submitted by citizen. Awaiting administrative review."
        ))

        # 7. Timeline Record (Section 88)
        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="SUBMITTED",
            message="Complaint submitted by citizen.",
            action_by=req.citizen_name or "Citizen",
            action_by_role="CITIZEN",
            message_type="SYSTEM"
        )

        # 8. Citizen In-App Notification (Section 89)
        if citizen_id:
            add_notification(
                conn=conn,
                user_id=citizen_id,
                complaint_id=complaint_id,
                title="Complaint Submitted",
                message=f"Complaint #{complaint_id} has been submitted successfully.",
                n_type="SUBMITTED"
            )

        conn.commit()
        conn.close()

        # Audit log creation
        audit_service.log_event(
            action="COMPLAINT_CREATED",
            entity_type="COMPLAINT",
            user_id=citizen_id,
            user_email=req.email,
            entity_id=complaint_id,
            new_value=f"Dept: {dept}, Priority: {priority}, Status: SUBMITTED"
        )

        return self.get_complaint_by_id(complaint_id)

    def get_complaint_by_id(self, complaint_id: str, current_user: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches full complaint details along with trace, status history, and timeline.
        Enforces server-side resource-level authorization (Section 59).
        Computes dynamic progress percentage and current stage number (Section 82 & 83).
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        complaint = dict(row)

        # Server-side resource authorization check
        if current_user:
            role = current_user.get("role")
            if role == "CITIZEN":
                if complaint["citizen_id"] != current_user["id"]:
                    conn.close()
                    raise PermissionError("Access Denied: You do not have permission to view other citizens' complaints.")
            elif role == "DEPARTMENT_OFFICER":
                officer_dept = current_user.get("department_name")
                comp_dept = complaint.get("department")
                if not officer_dept or not comp_dept or comp_dept.strip().lower() != officer_dept.strip().lower():
                    conn.close()
                    raise PermissionError(f"Access Denied: Complaint #{complaint_id} is assigned to '{comp_dept or 'Unassigned'}', not your department ('{officer_dept or 'None'}').")

        complaint["evidence_available"] = bool(complaint["evidence_available"])
        complaint["public_accessibility_affected"] = bool(complaint["public_accessibility_affected"])
        complaint["recurrence"] = bool(complaint["recurrence"])
        complaint["emergency"] = bool(complaint["emergency"])
        complaint["manual_override"] = bool(complaint["manual_override"])
        complaint["missing_info"] = json.loads(complaint["missing_info_json"] or "[]")
        complaint["conflicts"] = json.loads(complaint["conflicts_json"] or "[]")

        # Dynamic progress meter calculations (Section 82 & 83)
        norm_status = normalize_status(complaint.get("status"))
        complaint["status"] = norm_status
        stage_info = STAGE_PROGRESS.get(norm_status, (1, 20, "Complaint Submitted"))
        complaint["current_stage_number"] = stage_info[0]
        complaint["progress_percent"] = stage_info[1]
        complaint["status_display"] = stage_info[2]

        # Fetch traces
        cursor.execute("""
            SELECT step_order, step_type, rule_id, rule_name, conditions_evaluated_json, derived_fact_json, explanation
            FROM reasoning_traces
            WHERE complaint_id = ?
            ORDER BY step_order ASC
        """, (complaint_id,))
        trace_rows = cursor.fetchall()
        trace = []
        for t in trace_rows:
            trace.append({
                "step_order": t["step_order"],
                "step_type": t["step_type"],
                "rule_id": t["rule_id"],
                "rule_name": t["rule_name"],
                "conditions_evaluated": json.loads(t["conditions_evaluated_json"] or "{}"),
                "derived_fact": json.loads(t["derived_fact_json"] or "{}"),
                "explanation": t["explanation"]
            })
        complaint["reasoning_trace"] = trace

        # Ensure clean, updated explanation format
        curr_expl = str(complaint.get("explanation") or "")
        if "=== AI REASONING" in curr_expl or "Rule " in curr_expl or not curr_expl.strip():
            ground_facts = {
                "category": complaint.get("category"),
                "issue_type": complaint.get("issue_type"),
                "severity": complaint.get("severity"),
                "immediate_danger": complaint.get("immediate_danger"),
                "population_impact": complaint.get("affected_people"),
                "affected_people": complaint.get("affected_people"),
                "duration_days": complaint.get("duration_days"),
                "frequency": complaint.get("frequency"),
                "safety_risk": complaint.get("safety_risk"),
                "public_accessibility_affected": complaint.get("public_accessibility_affected"),
            }
            new_expl = self.agent.explanation_engine.build_narrative_explanation(
                ground_facts=ground_facts,
                trace=trace,
                selected_department=complaint.get("department"),
                selected_priority=complaint.get("priority", "LOW"),
                selected_escalation=complaint.get("escalation", "NO_ESCALATION"),
            )
            complaint["explanation"] = new_expl
            cursor.execute("UPDATE complaints SET explanation = ? WHERE complaint_id = ?", (new_expl, complaint_id))
            conn.commit()

        # Fetch status history
        cursor.execute("""
            SELECT previous_status, new_status, changed_by, notes, created_at
            FROM status_history
            WHERE complaint_id = ?
            ORDER BY id ASC
        """, (complaint_id,))
        complaint["status_history"] = [dict(h) for h in cursor.fetchall()]

        # Fetch complaint timeline (Section 88)
        cursor.execute("""
            SELECT id, complaint_id, status, message, message_type, action_by, action_by_role, created_at
            FROM complaint_timeline
            WHERE complaint_id = ?
            ORDER BY id ASC
        """, (complaint_id,))
        complaint["timeline"] = [dict(tm) for tm in cursor.fetchall()]

        # Fetch complaint_reasoning (Section 37)
        cursor.execute("SELECT * FROM complaint_reasoning WHERE complaint_id = ?", (complaint_id,))
        reas_row = cursor.fetchone()
        if reas_row:
            complaint["csp_result"] = {
                "input_facts": json.loads(reas_row["input_facts"] or "{}"),
                "constraints_checked": json.loads(reas_row["constraints_checked"] or "[]"),
                "CSP_result": json.loads(reas_row["CSP_result"] or "{}"),
                "rules_evaluated": json.loads(reas_row["rules_evaluated"] or "[]"),
                "rules_fired": json.loads(reas_row["rules_fired"] or "[]"),
                "derived_facts": json.loads(reas_row["derived_facts"] or "{}"),
                "final_conclusions": json.loads(reas_row["final_conclusions"] or "{}"),
                "explanation": reas_row["explanation"]
            }
        else:
            complaint["csp_result"] = None

        # Fetch complaint_messages (Section 33)
        cursor.execute("""
            SELECT id, complaint_id, admin_id, message, message_type, created_at
            FROM complaint_messages
            WHERE complaint_id = ?
            ORDER BY id ASC
        """, (complaint_id,))
        complaint["messages"] = [dict(m) for m in cursor.fetchall()]

        conn.close()
        return complaint

    def get_all_complaints(
        self,
        current_user: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        department: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries complaints with mandatory server-side role scoping (Section 47 & 59).
        - CITIZEN: restricted to citizen_id == user.id
        - DEPARTMENT_OFFICER: restricted to department == user.department_name
        - ADMIN: full visibility
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM complaints WHERE 1=1"
        params = []

        # Server-Side RBAC Filtering
        if current_user:
            role = current_user.get("role")
            if role == "CITIZEN":
                query += " AND citizen_id = ?"
                params.append(current_user["id"])
            elif role == "DEPARTMENT_OFFICER":
                officer_dept = current_user.get("department_name")
                if officer_dept:
                    query += " AND LOWER(department) = LOWER(?)"
                    params.append(officer_dept)

        if category:
            query += " AND category = ?"
            params.append(category)
        if department and (not current_user or current_user.get("role") == "ADMIN"):
            query += " AND department = ?"
            params.append(department)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if status:
            norm_filter = normalize_status(status)
            matched_statuses = {status, norm_filter}
            for k, v in LEGACY_STATUS_MAP.items():
                if v == norm_filter:
                    matched_statuses.add(k)
            placeholders = ",".join("?" for _ in matched_statuses)
            query += f" AND status IN ({placeholders})"
            params.extend(list(matched_statuses))
        if search:
            query += " AND (complaint_id LIKE ? OR citizen_name LIKE ? OR location LIKE ? OR issue_type LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param])

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            item = dict(r)
            item["evidence_available"] = bool(item["evidence_available"])
            item["public_accessibility_affected"] = bool(item["public_accessibility_affected"])
            item["recurrence"] = bool(item["recurrence"])
            item["emergency"] = bool(item["emergency"])
            item["manual_override"] = bool(item["manual_override"])
            item["missing_info"] = json.loads(item["missing_info_json"] or "[]")
            item["conflicts"] = json.loads(item["conflicts_json"] or "[]")
            item["explanation"] = (item.get("explanation") or "").replace("Rule None specifies that", "Rule ER005 specifies that")

            norm_status = normalize_status(item.get("status"))
            item["status"] = norm_status
            stage_info = STAGE_PROGRESS.get(norm_status, (1, 20, "Complaint Submitted"))
            item["current_stage_number"] = stage_info[0]
            item["progress_percent"] = stage_info[1]
            item["status_display"] = stage_info[2]

            results.append(item)

        conn.close()
        return results

    # ==============================================================
    # 5-STAGE LIFECYCLE STATE MACHINE ACTIONS
    # ==============================================================

    def acknowledge_complaint(
        self,
        complaint_id: str,
        notes: Optional[str],
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 1 -> 2: SUBMITTED -> ACKNOWLEDGED (Section 74).
        Admin acknowledges receipt of grievance.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        current_st = normalize_status(curr["status"])
        if current_st != "SUBMITTED":
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"SUBMITTED -> ACKNOWLEDGED. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        admin_name = current_user.get("name", "Administrator")
        msg = notes or "Complaint acknowledged by administration."

        cursor.execute("""
            UPDATE complaints SET status = 'ACKNOWLEDGED', updated_at = ?
            WHERE complaint_id = ?
        """, (now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'SUBMITTED', 'ACKNOWLEDGED', ?, ?)
        """, (complaint_id, admin_name, msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="ACKNOWLEDGED",
            message=msg,
            action_by=admin_name,
            action_by_role="ADMIN",
            message_type="ACKNOWLEDGEMENT"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=msg,
            message_type="ACKNOWLEDGEMENT"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Complaint Acknowledged",
            message=f"Your complaint #{complaint_id} has been acknowledged by administration.",
            n_type="ACKNOWLEDGEMENT"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="COMPLAINT_ACKNOWLEDGED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="SUBMITTED",
            new_value="ACKNOWLEDGED",
            reason=msg
        )

        return self.get_complaint_by_id(complaint_id)

    def accept_complaint(
        self,
        complaint_id: str,
        department: Optional[str],
        priority: Optional[str],
        message: str,
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 2 -> 3: ACKNOWLEDGED -> ACCEPTED (Section 75 & 76).
        Admin reviews complaint, accepts it for action, and enters response description.
        """
        if not message or not message.strip():
            raise ValueError("Acceptance / response message to citizen is required.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status, department, priority FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        current_st = normalize_status(curr["status"])
        if current_st != "ACKNOWLEDGED":
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"ACKNOWLEDGED -> ACCEPTED. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        admin_name = current_user.get("name", "Administrator")
        target_dept = department or curr["department"]
        target_priority = priority or curr["priority"]
        clean_msg = message.strip()

        cursor.execute("""
            UPDATE complaints
            SET status = 'ACCEPTED', department = ?, priority = ?, admin_message = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (target_dept, target_priority, clean_msg, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'ACKNOWLEDGED', 'ACCEPTED', ?, ?)
        """, (complaint_id, admin_name, clean_msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="ACCEPTED",
            message=clean_msg,
            action_by=admin_name,
            action_by_role="ADMIN",
            message_type="ACCEPTANCE"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="ACCEPTANCE"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Complaint Accepted",
            message=f"Your complaint #{complaint_id} has been accepted: {clean_msg}",
            n_type="ACCEPTANCE"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="COMPLAINT_ACCEPTED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="ACKNOWLEDGED",
            new_value="ACCEPTED",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    def start_work(
        self,
        complaint_id: str,
        message: Optional[str],
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 3 -> 4: ACCEPTED -> IN_PROGRESS (Section 77).
        Admin starts work and records work started description.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status, department FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        # RBAC Check: Department Officer can only operate on complaints assigned to their department
        if current_user and current_user.get("role") == "DEPARTMENT_OFFICER":
            officer_dept = current_user.get("department_name")
            comp_dept = curr["department"]
            if not officer_dept or not comp_dept or comp_dept.strip().lower() != officer_dept.strip().lower():
                conn.close()
                raise PermissionError(f"Access Denied: Complaint #{complaint_id} is assigned to '{comp_dept or 'Unassigned'}', not your department ('{officer_dept or 'None'}').")

        current_st = normalize_status(curr["status"])
        if current_st not in ("ACCEPTED", "ACKNOWLEDGED"):
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"ACKNOWLEDGED -> IN_PROGRESS. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        user_name = current_user.get("name", "Administrator")
        user_role = current_user.get("role", "ADMIN")
        clean_msg = (message and message.strip()) or "The maintenance team has been assigned and inspection has started."

        cursor.execute("""
            UPDATE complaints
            SET status = 'IN_PROGRESS', work_started_message = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (clean_msg, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'ACCEPTED', 'IN_PROGRESS', ?, ?)
        """, (complaint_id, user_name, clean_msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="IN_PROGRESS",
            message=clean_msg,
            action_by=user_name,
            action_by_role=user_role,
            message_type="PROGRESS_UPDATE"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="PROGRESS_UPDATE"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Work in Progress",
            message=f"Work on complaint #{complaint_id} is in progress: {clean_msg}",
            n_type="IN_PROGRESS"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="WORK_STARTED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="ACCEPTED",
            new_value="IN_PROGRESS",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    def add_progress_update(
        self,
        complaint_id: str,
        message: str,
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Progress updates while IN_PROGRESS (Section 78).
        Multiple updates allowed without changing stage from IN_PROGRESS.
        """
        if not message or not message.strip():
            raise ValueError("Progress update message cannot be empty.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status, department FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        # RBAC Check: Department Officer can only operate on complaints assigned to their department
        if current_user and current_user.get("role") == "DEPARTMENT_OFFICER":
            officer_dept = current_user.get("department_name")
            comp_dept = curr["department"]
            if not officer_dept or not comp_dept or comp_dept.strip().lower() != officer_dept.strip().lower():
                conn.close()
                raise PermissionError(f"Access Denied: Complaint #{complaint_id} is assigned to '{comp_dept or 'Unassigned'}', not your department ('{officer_dept or 'None'}').")

        current_st = normalize_status(curr["status"])
        if current_st != "IN_PROGRESS":
            conn.close()
            raise ValueError(
                f"Progress updates can only be added while work is in progress (status: IN_PROGRESS). "
                f"Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        user_name = current_user.get("name", "Administrator")
        user_role = current_user.get("role", "ADMIN")
        clean_msg = message.strip()

        cursor.execute("UPDATE complaints SET updated_at = ? WHERE complaint_id = ?", (now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'IN_PROGRESS', 'IN_PROGRESS', ?, ?)
        """, (complaint_id, user_name, f"Progress Update: {clean_msg}"))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="IN_PROGRESS",
            message=clean_msg,
            action_by=user_name,
            action_by_role=user_role,
            message_type="PROGRESS_UPDATE"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="PROGRESS_UPDATE"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Progress Update",
            message=f"Update on complaint #{complaint_id}: {clean_msg}",
            n_type="PROGRESS_UPDATE"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="PROGRESS_UPDATE_ADDED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="IN_PROGRESS",
            new_value="IN_PROGRESS",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    def complete_work(
        self,
        complaint_id: str,
        completion_message: str,
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 4 -> 5: IN_PROGRESS -> WORK_COMPLETED (Section 79).
        Requires completion description. Citizen is NOT considered informed yet (Section 93).
        """
        if not completion_message or not completion_message.strip():
            raise ValueError("Work completion description is required.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status, department FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        # RBAC Check: Department Officer can only operate on complaints assigned to their department
        if current_user and current_user.get("role") == "DEPARTMENT_OFFICER":
            officer_dept = current_user.get("department_name")
            comp_dept = curr["department"]
            if not officer_dept or not comp_dept or comp_dept.strip().lower() != officer_dept.strip().lower():
                conn.close()
                raise PermissionError(f"Access Denied: Complaint #{complaint_id} is assigned to '{comp_dept or 'Unassigned'}', not your department ('{officer_dept or 'None'}').")

        current_st = normalize_status(curr["status"])
        if current_st != "IN_PROGRESS":
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"IN_PROGRESS -> WORK_COMPLETED. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        user_name = current_user.get("name", "Administrator")
        user_role = current_user.get("role", "ADMIN")
        clean_msg = completion_message.strip()

        cursor.execute("""
            UPDATE complaints
            SET status = 'WORK_COMPLETED', completion_message = ?, completed_by = ?, completed_at = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (clean_msg, user_name, now_str, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'IN_PROGRESS', 'WORK_COMPLETED', ?, ?)
        """, (complaint_id, user_name, clean_msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="WORK_COMPLETED",
            message=clean_msg,
            action_by=user_name,
            action_by_role=user_role,
            message_type="COMPLETION"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="COMPLETION"
        )

        # Inform internal audit that work completed (citizen will be notified in stage 6)
        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Work Completed",
            message=f"Work on complaint #{complaint_id} has been completed and is awaiting administrative validation.",
            n_type="WORK_COMPLETED"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="WORK_COMPLETED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="IN_PROGRESS",
            new_value="WORK_COMPLETED",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    def inform_user(
        self,
        complaint_id: str,
        notification_message: str,
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 5 -> 6: WORK_COMPLETED -> USER_INFORMED (Section 80 & 93).
        Admin explicitly transmits completion and resolution notice to citizen.
        """
        if not notification_message or not notification_message.strip():
            raise ValueError("Notification message to citizen is required.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        current_st = normalize_status(curr["status"])
        if current_st != "WORK_COMPLETED":
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"WORK_COMPLETED -> USER_INFORMED. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        admin_name = current_user.get("name", "Administrator")
        clean_msg = notification_message.strip()

        cursor.execute("""
            UPDATE complaints
            SET status = 'USER_INFORMED', notification_message = ?, resolution_message = ?, informed_by = ?, informed_at = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (clean_msg, clean_msg, admin_name, now_str, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'WORK_COMPLETED', 'USER_INFORMED', ?, ?)
        """, (complaint_id, admin_name, clean_msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="USER_INFORMED",
            message=clean_msg,
            action_by=admin_name,
            action_by_role="ADMIN",
            message_type="COMPLETION"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="FINAL_RESPONSE"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Your Complaint Has Been Resolved",
            message=f"Please review the completion details: {clean_msg}",
            n_type="USER_INFORMED"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="USER_INFORMED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="WORK_COMPLETED",
            new_value="USER_INFORMED",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    def close_complaint(
        self,
        complaint_id: str,
        closure_message: Optional[str],
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage Transition 6 -> 7: USER_INFORMED -> CLOSED (Section 81).
        Formally closes complaint after confirmation. Read-only for normal users.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT citizen_id, status FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        current_st = normalize_status(curr["status"])
        if current_st not in ("USER_INFORMED", "RESOLVED", "WORK_COMPLETED"):
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"RESOLVED -> CLOSED. Current stage is '{current_st}'."
            )

        now_str = datetime.now().isoformat()
        admin_name = current_user.get("name", "Administrator")
        clean_msg = (closure_message and closure_message.strip()) or "Complaint lifecycle formally closed by administration."

        cursor.execute("""
            UPDATE complaints
            SET status = 'CLOSED', closure_message = ?, closed_by = ?, closed_at = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (clean_msg, admin_name, now_str, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'USER_INFORMED', 'CLOSED', ?, ?)
        """, (complaint_id, admin_name, clean_msg))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="CLOSED",
            message=clean_msg,
            action_by=admin_name,
            action_by_role="ADMIN",
            message_type="CLOSURE"
        )

        add_complaint_message(
            conn=conn,
            complaint_id=complaint_id,
            admin_id=current_user.get("id"),
            message=clean_msg,
            message_type="CLOSURE"
        )

        add_notification(
            conn=conn,
            user_id=curr["citizen_id"],
            complaint_id=complaint_id,
            title="Complaint Closed",
            message=f"Complaint #{complaint_id} has been formally closed: {clean_msg}",
            n_type="CLOSED"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="COMPLAINT_CLOSED",
            entity_type="COMPLAINT",
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            entity_id=complaint_id,
            old_value="USER_INFORMED",
            new_value="CLOSED",
            reason=clean_msg
        )

        return self.get_complaint_by_id(complaint_id)

    # ==============================================================
    # LEGACY WRAPPERS & VALIDATORS (Section 87)
    # ==============================================================

    def update_complaint_status(
        self,
        complaint_id: str,
        new_status: str,
        notes: Optional[str],
        changed_by: str,
        current_user: Optional[Dict[str, Any]] = None,
        resolution_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transitions status with strict backend transition validation (Section 87).
        Rejects arbitrary jumps like SUBMITTED -> CLOSED with ValueError.
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT status, department FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        old_status = normalize_status(curr["status"])
        target_status = normalize_status(new_status)

        # Transition validation (Section 87 & 94)
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if target_status not in allowed:
            conn.close()
            raise ValueError(
                f"Invalid status transition. Complaint must progress through the required stages: "
                f"SUBMITTED -> ACKNOWLEDGED -> IN_PROGRESS -> RESOLVED -> CLOSED. "
                f"Cannot jump from '{old_status}' to '{target_status}'."
            )

        # Route to specific lifecycle handler
        user_ctx = current_user or {"name": changed_by, "role": "ADMIN", "id": None, "email": None}
        conn.close()

        if target_status == "ACKNOWLEDGED":
            return self.acknowledge_complaint(complaint_id, notes, user_ctx)
        elif target_status == "ACCEPTED":
            return self.accept_complaint(complaint_id, None, None, notes or "Complaint accepted.", user_ctx)
        elif target_status == "IN_PROGRESS":
            return self.start_work(complaint_id, notes, user_ctx)
        elif target_status == "WORK_COMPLETED":
            return self.complete_work(complaint_id, notes or resolution_message or "Work completed.", user_ctx)
        elif target_status == "USER_INFORMED":
            return self.inform_user(complaint_id, resolution_message or notes or "User informed of completion.", user_ctx)
        elif target_status == "CLOSED":
            return self.close_complaint(complaint_id, notes or "Complaint closed.", user_ctx)

        return self.get_complaint_by_id(complaint_id)

    def assign_department_by_admin(
        self,
        complaint_id: str,
        department: str,
        priority: Optional[str],
        notes: Optional[str],
        current_user: Dict[str, Any],
        admin_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Maps admin assignment to ACKNOWLEDGED -> ACCEPTED.
        If complaint is currently SUBMITTED, automatically transitions through ACKNOWLEDGED first.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        conn.close()
        if not curr:
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        current_st = normalize_status(curr["status"])
        if current_st == "SUBMITTED":
            self.acknowledge_complaint(complaint_id, "Complaint received and acknowledged by administration.", current_user)

        msg = admin_message or notes or f"Grievance accepted and assigned to {department}."
        return self.accept_complaint(complaint_id, department, priority, msg, current_user)

    def override_department(
        self,
        complaint_id: str,
        new_dept: str,
        reason: str,
        officer_name: str,
        current_user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Admin-only manual department override.
        Preserves original AI decision and trace, logs override metadata (Section 56).
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT department, ai_department FROM complaints WHERE complaint_id = ?", (complaint_id,))
        curr = cursor.fetchone()
        if not curr:
            conn.close()
            raise ValueError(f"Complaint '{complaint_id}' not found.")

        old_dept = curr["department"]
        now_dt = datetime.now()
        now_str = now_dt.isoformat()

        cursor.execute("""
            UPDATE complaints
            SET department = ?, manual_override = 1, manual_department = ?,
                manual_override_reason = ?, overridden_by = ?, override_timestamp = ?, updated_at = ?
            WHERE complaint_id = ?
        """, (new_dept, new_dept, reason, officer_name, now_str, now_str, complaint_id))

        cursor.execute("""
            INSERT INTO status_history (complaint_id, previous_status, new_status, changed_by, notes)
            VALUES (?, 'ACCEPTED', 'ACCEPTED', ?, ?)
        """, (
            complaint_id,
            officer_name,
            f"Department manually changed from '{old_dept}' to '{new_dept}'. Reason: {reason}"
        ))

        add_timeline_entry(
            conn=conn,
            complaint_id=complaint_id,
            status="ACCEPTED",
            message=f"Department override: {old_dept} -> {new_dept}. Reason: {reason}",
            action_by=officer_name,
            action_by_role="ADMIN",
            message_type="SYSTEM"
        )

        conn.commit()
        conn.close()

        audit_service.log_event(
            action="DEPARTMENT_OVERRIDE",
            entity_type="COMPLAINT",
            user_id=current_user["id"] if current_user else None,
            user_email=current_user["email"] if current_user else officer_name,
            entity_id=complaint_id,
            old_value=old_dept,
            new_value=new_dept,
            reason=reason
        )

        return self.get_complaint_by_id(complaint_id)

    # ==============================================================
    # TIMELINE & NOTIFICATION HELPERS (Section 88 & 89)
    # ==============================================================

    def get_timeline(self, complaint_id: str, current_user: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self.get_complaint_by_id(complaint_id, current_user=current_user)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, complaint_id, status, message, message_type, action_by, action_by_role, created_at
            FROM complaint_timeline
            WHERE complaint_id = ?
            ORDER BY id ASC
        """, (complaint_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_notifications(self, user_id: int) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, complaint_id, title, message, type, is_read, created_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))
        items = [dict(r) for r in cursor.fetchall()]
        for it in items:
            it["is_read"] = bool(it["is_read"])
        unread_count = sum(1 for it in items if not it["is_read"])
        conn.close()
        return {"notifications": items, "unread_count": unread_count}

    def mark_notification_read(self, notification_id: int, user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?", (notification_id, user_id))
        conn.commit()
        conn.close()

    def mark_all_notifications_read(self, user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


complaint_service = ComplaintService()
