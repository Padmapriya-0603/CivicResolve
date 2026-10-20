"""
Pydantic schemas and data validation models for API requests and responses.
Includes strict type checking, RBAC models, and custom constraint satisfaction validators.
"""

from typing import List, Optional, Dict, Any
import re
from pydantic import BaseModel, Field, field_validator

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def check_email(v: str) -> str:
    cleaned = str(v).strip().lower()
    if not EMAIL_PATTERN.match(cleaned):
        raise ValueError("Invalid email address format.")
    return cleaned


# ==========================================
# 1. User & Authentication Schemas
# ==========================================
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(...)
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)


class UserLoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str
    department_id: Optional[str] = None
    department_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: str
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class UserCreateAdminRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(...)
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = None
    role: str = Field(..., description="CITIZEN, DEPARTMENT_OFFICER, ADMIN")
    department_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"CITIZEN", "DEPARTMENT_OFFICER", "ADMIN"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid role '{v}'. Permitted: {valid}")
        return upper


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class UserRoleUpdateRequest(BaseModel):
    role: str
    department_id: Optional[str] = None


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: str = Field(...)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)


class ForgotPasswordResponse(BaseModel):
    message: str
    email: str
    reset_code: Optional[str] = None
    expires_in_minutes: int = 15


class ResetPasswordRequest(BaseModel):
    email: str = Field(...)
    reset_code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)


class ResetPasswordResponse(BaseModel):
    message: str
    email: str


# ==========================================
# 2. Audit Log Schema
# ==========================================
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    timestamp: str


# ==========================================
# 3. Department Admin Management Schemas
# ==========================================
class DepartmentCreateRequest(BaseModel):
    department_id: str = Field(..., min_length=3)
    name: str = Field(..., min_length=3)
    description: str = Field(...)
    supported_issues: List[str] = Field(default_factory=list)
    escalation_authority: str = Field(...)
    is_active: bool = True


class DepartmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    supported_issues: Optional[List[str]] = None
    escalation_authority: Optional[str] = None
    is_active: Optional[bool] = None


# ==========================================
# 4. Grievance Complaint Schemas
# ==========================================
class ComplaintCreateRequest(BaseModel):
    # Citizen Info
    citizen_name: str = Field(..., min_length=2, max_length=100, description="Full name of citizen")
    phone: str = Field(..., min_length=7, max_length=20, description="Contact phone number")
    email: str = Field(..., description="Valid email address")
    zone: Optional[str] = Field(None, description="Municipal zone identifier (e.g. Zone 8 - Anna Nagar)")
    ward: str = Field(..., min_length=1, max_length=100, description="Municipal ward or area identifier")
    location: str = Field(..., min_length=3, max_length=200, description="Exact landmark or street address")
    preferred_contact: str = Field("Phone", description="Preferred contact method")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return check_email(v)

    # Complaint Category & Issue
    category: str = Field(..., description="High-level grievance category")
    issue_type: str = Field(..., description="Specific predefined issue type within category")

    # Additional Structured Attributes (Sections 6, 8, 9)
    location_type: Optional[str] = Field("Public Road", description="Location classification: Public Road, Residential, Commercial, etc.")
    immediate_danger: Optional[str] = Field("NO", description="Immediate danger: YES or NO")
    problem_type: Optional[str] = Field(None, description="Problem type (synonym for issue_type)")
    description: Optional[str] = Field(None, description="Free text context for admin view (not processed by NLP)")
    duration_days: Optional[int] = Field(None, description="Number of days the issue has persisted (must be >= 0)")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    affected_people: Optional[int] = Field(None, description="Estimated number of affected citizens (must be >= 0)")
    frequency: str = Field(..., description="Frequency: ONE_TIME, OCCASIONAL, FREQUENT, CONTINUOUS")
    evidence_available: bool = Field(False, description="Whether supporting document/photo was provided")
    evidence_filename: Optional[str] = Field(None, description="Filename of uploaded evidence")
    safety_risk: str = Field(..., description="Safety hazard level: NONE, LOW, MEDIUM, HIGH, CRITICAL")
    public_accessibility_affected: bool = Field(False, description="Whether public transit or road access is impeded")
    recurrence: bool = Field(False, description="Whether this issue has happened before")
    emergency: bool = Field(False, description="Citizen-flagged immediate hazard")

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Duration in days cannot be negative.")
        return v

    @field_validator("affected_people")
    @classmethod
    def validate_affected_people(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Affected people count cannot be negative.")
        return v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid severity '{v}'. Must be one of: {', '.join(sorted(valid))}")
        return upper

    @field_validator("safety_risk")
    @classmethod
    def validate_safety_risk(cls, v: str) -> str:
        valid = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid safety risk '{v}'. Must be one of: {', '.join(sorted(valid))}")
        return upper

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        valid = {"ONE_TIME", "OCCASIONAL", "FREQUENT", "CONTINUOUS"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid frequency '{v}'. Must be one of: {', '.join(sorted(valid))}")
        return upper


class ComplaintValidateRequest(BaseModel):
    category: str
    issue_type: str
    duration_days: Optional[int] = None
    affected_people: Optional[int] = None
    severity: Optional[str] = None
    safety_risk: Optional[str] = None
    emergency: Optional[bool] = None
    frequency: Optional[str] = None


class ValidationResultResponse(BaseModel):
    valid: bool
    violations: List[str] = []
    warnings: List[str] = []


class StatusUpdateRequest(BaseModel):
    status: str = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Optional transition notes")
    changed_by: Optional[str] = Field(None, description="Officer updating")
    resolution_message: Optional[str] = Field(None, description="Message sent to citizen upon task completion")


class ComplaintAssignRequest(BaseModel):
    department: str = Field(..., description="Department assigned by admin")
    priority: Optional[str] = Field(None, description="Optional priority level confirmed by admin")
    notes: Optional[str] = Field(None, description="Administrative assignment / dispatch instructions")
    admin_message: Optional[str] = Field(None, description="Description/message sent by admin to citizen upon acceptance")


class DepartmentOverrideRequest(BaseModel):
    department: str = Field(..., description="New manually assigned department")
    reason: str = Field(..., min_length=5, description="Reason for overriding AI decision")
    officer_name: Optional[str] = Field(None, description="Officer performing override")


class ReasoningTraceStepResponse(BaseModel):
    step_order: int
    step_type: str
    rule_id: Optional[str] = None
    rule_name: Optional[str] = None
    conditions_evaluated: Optional[Dict[str, Any]] = None
    derived_fact: Optional[Dict[str, Any]] = None
    explanation: str


class ConflictDetail(BaseModel):
    conflict_type: str
    description: str
    conflicting_elements: List[str]
    resolution: Optional[str] = None
    is_blocking: bool = False


class StatusHistoryItemResponse(BaseModel):
    previous_status: Optional[str] = None
    new_status: str
    changed_by: Optional[str] = "SYSTEM"
    notes: Optional[str] = None
    created_at: Optional[str] = None


class TimelineItemResponse(BaseModel):
    id: int
    complaint_id: str
    status: str
    message: str
    message_type: Optional[str] = "SYSTEM"
    action_by: Optional[str] = "SYSTEM"
    action_by_role: Optional[str] = "SYSTEM"
    created_at: Optional[str] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    complaint_id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: str


class AcknowledgeRequest(BaseModel):
    notes: Optional[str] = Field(None, description="Optional acknowledgement notes")


class AcceptRequest(BaseModel):
    department: Optional[str] = Field(None, description="Assigned department")
    priority: Optional[str] = Field(None, description="Confirmed priority")
    message: str = Field(..., min_length=3, description="Response / acceptance message sent to citizen")


class StartWorkRequest(BaseModel):
    message: Optional[str] = Field(None, description="Work started description sent to citizen")


class ProgressUpdateRequest(BaseModel):
    message: str = Field(..., min_length=3, description="Progress update message")


class CompleteWorkRequest(BaseModel):
    completion_message: str = Field(..., min_length=3, description="Completion description")


class InformUserRequest(BaseModel):
    notification_message: str = Field(..., min_length=3, description="Final response / notification message sent to citizen")


class CloseComplaintRequest(BaseModel):
    closure_message: Optional[str] = Field(None, description="Formal closure message")


class ComplaintResponse(BaseModel):
    complaint_id: str
    citizen_id: Optional[int] = None
    citizen_name: str
    phone: str
    email: str
    zone: Optional[str] = None
    ward: str
    location: str
    preferred_contact: str
    category: str
    issue_type: str
    duration_days: Optional[int] = None
    severity: str
    affected_people: Optional[int] = None
    frequency: str
    evidence_available: bool = False
    evidence_filename: Optional[str] = None
    safety_risk: str
    public_accessibility_affected: bool = False
    recurrence: bool = False
    emergency: bool = False
    department: Optional[str] = None
    ai_department: Optional[str] = None
    manual_override: bool = False
    manual_department: Optional[str] = None
    manual_override_reason: Optional[str] = None
    overridden_by: Optional[str] = None
    override_timestamp: Optional[str] = None
    priority: str
    escalation: str
    status: str
    status_display: Optional[str] = None
    current_stage_number: Optional[int] = 1
    progress_percent: Optional[int] = 14
    missing_info: List[str] = []
    conflicts: List[ConflictDetail] = []
    explanation: Optional[str] = None
    created_at: str
    updated_at: str
    reasoning_trace: Optional[List[ReasoningTraceStepResponse]] = None
    status_history: Optional[List[StatusHistoryItemResponse]] = None
    timeline: Optional[List[TimelineItemResponse]] = None
    admin_message: Optional[str] = None
    resolution_message: Optional[str] = None
    work_started_message: Optional[str] = None
    completion_message: Optional[str] = None
    completed_by: Optional[str] = None
    completed_at: Optional[str] = None
    notification_message: Optional[str] = None
    informed_by: Optional[str] = None
    informed_at: Optional[str] = None
    closure_message: Optional[str] = None
    closed_by: Optional[str] = None
    closed_at: Optional[str] = None
    complaint_number: Optional[str] = None
    location_type: Optional[str] = "Public Road"
    immediate_danger: Optional[str] = "NO"
    description: Optional[str] = None
    csp_result: Optional[Dict[str, Any]] = None
    messages: Optional[List[Dict[str, Any]]] = None



class RuleResponse(BaseModel):
    rule_id: str
    rule_name: str
    rule_type: str
    description: str
    conditions: Dict[str, Any]
    conclusion: Dict[str, Any]
    priority_order: int
    is_active: bool


class DepartmentResponse(BaseModel):
    department_id: str
    name: str
    description: str
    supported_issues: List[str]
    escalation_authority: str
    is_active: bool


class CategoryResponse(BaseModel):
    category_id: str
    name: str
    description: str


class IssueTypeResponse(BaseModel):
    issue_type_id: str
    category_id: str
    name: str
    description: str
    default_department_id: str


class DashboardStatsResponse(BaseModel):
    total_complaints: int
    new_complaints: int
    submitted_complaints: Optional[int] = 0
    acknowledged_complaints: Optional[int] = 0
    accepted_complaints: Optional[int] = 0
    assigned_complaints: Optional[int] = 0
    in_progress_complaints: int
    work_completed_complaints: Optional[int] = 0
    user_informed_complaints: Optional[int] = 0
    resolved_complaints: int
    closed_complaints: Optional[int] = 0
    critical_complaints: int
    high_priority_complaints: int
    escalated_complaints: int
    by_department: Dict[str, int]
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]
    bottlenecks: Optional[Dict[str, Any]] = None
    queues: Optional[Dict[str, int]] = None
    # Admin system counters
    total_users: Optional[int] = None
    total_citizens: Optional[int] = None
    total_officers: Optional[int] = None
    total_departments: Optional[int] = None


class RuleCreateRequest(BaseModel):
    rule_id: str
    rule_name: str
    rule_type: str = "ROUTING"
    description: str
    conditions: Dict[str, Any]
    conclusion: Dict[str, Any]
    priority_order: int = 10
    is_active: bool = True


class RuleUpdateRequest(BaseModel):
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    conclusion: Optional[Dict[str, Any]] = None
    priority_order: Optional[int] = None
    is_active: Optional[bool] = None


class AdminUserUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[str] = None
    is_active: Optional[bool] = None

