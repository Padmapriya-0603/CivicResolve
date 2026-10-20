"""
FastAPI Main Application for AI-Based Public Grievance Routing & Reasoning System.
Includes complete Role-Based Access Control (RBAC), JWT Authentication,
Audit Logging, User Management, and Server-Side Resource Scoping.
"""

import os
import re
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from database import init_db, get_db_connection
from seed_data import seed_database
from models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
    UserResponse,
    UserCreateAdminRequest,
    UserStatusUpdateRequest,
    UserRoleUpdateRequest,
    UserProfileUpdateRequest,
    AuditLogResponse,
    DepartmentCreateRequest,
    DepartmentUpdateRequest,
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintValidateRequest,
    ValidationResultResponse,
    StatusUpdateRequest,
    ComplaintAssignRequest,
    DepartmentOverrideRequest,
    RuleResponse,
    DepartmentResponse,
    CategoryResponse,
    IssueTypeResponse,
    DashboardStatsResponse,
    ReasoningTraceStepResponse,
    TimelineItemResponse,
    NotificationResponse,
    AcknowledgeRequest,
    AcceptRequest,
    StartWorkRequest,
    ProgressUpdateRequest,
    CompleteWorkRequest,
    InformUserRequest,
    CloseComplaintRequest,
    RuleCreateRequest,
    RuleUpdateRequest,
    AdminUserUpdateRequest
)
from utils.security import hash_password, verify_password, create_access_token, generate_reset_code
from utils.dependencies import (
    get_current_user,
    require_roles,
    require_citizen,
    require_officer,
    require_admin,
    require_officer_or_admin,
    require_any_authenticated
)
from services.complaint_service import complaint_service
from services.dashboard_service import dashboard_service
from services.audit_service import audit_service
from utils.validators import validate_complaint_constraints, CATEGORY_ISSUE_MAP
from utils.chennai_zones import get_all_zones, get_wards_for_zone, get_zone_by_name_or_id
from ai.knowledge_base import DEPARTMENTS_KB, PRIORITY_PRECEDENCE, ESCALATION_PRECEDENCE
from ai.rules import get_default_rules

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed data on startup without wiping existing complaints
    init_db()
    seed_database(clean_complaints=False)
    yield


app = FastAPI(
    title="Public Grievance Routing & Reasoning System (Classical AI & RBAC)",
    description="Deterministic and explainable public grievance routing powered by forward chaining, constraint satisfaction, and role-based access control.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 1. Health Endpoint
# ==========================================
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "system": "AI-Based Public Grievance Routing & Reasoning System",
        "engine": "Classical AI (Forward Chaining & CSP)",
        "rbac_enabled": True,
        "roles_supported": ["CITIZEN", "DEPARTMENT_OFFICER", "ADMIN"],
        "ml_nlp_free": True,
        "statement": "The system provides deterministic and explainable grievance routing based on structured inputs, a predefined knowledge base, and a rule set."
    }


# ==========================================
# 2. Authentication & Profile Endpoints
# ==========================================
@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_citizen(req: UserRegisterRequest):
    """Registers a new citizen account and returns an authenticated JWT session."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing email
    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email.lower(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    pw_hash = hash_password(req.password)
    cursor.execute("""
        INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
        VALUES (?, ?, ?, ?, 'CITIZEN', NULL, 1)
    """, (req.name, req.email.lower(), req.phone, pw_hash))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Log audit event
    audit_service.log_event(
        action="USER_REGISTRATION",
        entity_type="USER",
        user_id=new_id,
        user_email=req.email.lower(),
        entity_id=str(new_id),
        new_value="Role: CITIZEN"
    )

    # Issue JWT token
    token = create_access_token({
        "user_id": new_id,
        "email": req.email.lower(),
        "role": "CITIZEN",
        "department_id": None
    })

    return TokenResponse(
        access_token=token,
        user_id=new_id,
        name=req.name,
        email=req.email.lower(),
        role="CITIZEN",
        department_id=None,
        department_name=None
    )


@app.post("/api/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login_user(req: UserLoginRequest):
    """Authenticates a user by email and password, returning a signed JWT token."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.password_hash, u.role, u.department_id, u.is_active, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.email = ?
    """, (req.email.lower(),))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password."
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently inactive. Contact the administrator."
        )

    # Issue JWT token
    token = create_access_token({
        "user_id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "department_id": user["department_id"]
    })

    audit_service.log_event(
        action="LOGIN_SUCCESS",
        entity_type="AUTH",
        user_id=user["id"],
        user_email=user["email"],
        new_value=f"Role: {user['role']}"
    )

    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        department_id=user["department_id"],
        department_name=user["department_name"]
    )


@app.post("/api/auth/forgot-password", response_model=ForgotPasswordResponse, tags=["Authentication"])
def forgot_password(req: ForgotPasswordRequest):
    """
    Initiates the password reset workflow by generating a time-limited 6-digit verification code.
    Logs audit event and stores code in password_resets table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, is_active FROM users WHERE email = ?
    """, (req.email.lower(),))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address."
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is deactivated. Please contact municipal administration."
        )

    # Invalidate any existing unused reset codes for this email
    cursor.execute("UPDATE password_resets SET used = 1 WHERE email = ? AND used = 0", (req.email.lower(),))

    reset_code = generate_reset_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    cursor.execute("""
        INSERT INTO password_resets (email, reset_code, expires_at, used)
        VALUES (?, ?, ?, 0)
    """, (req.email.lower(), reset_code, expires_at.isoformat()))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="PASSWORD_RESET_REQUESTED",
        entity_type="AUTH",
        user_id=user["id"],
        user_email=user["email"],
        new_value="6-digit reset verification code generated (expires in 15 mins)"
    )

    return ForgotPasswordResponse(
        message="A password reset verification code has been generated. Enter the code and your new password to complete the reset.",
        email=user["email"],
        reset_code=reset_code,
        expires_in_minutes=15
    )


@app.post("/api/auth/reset-password", response_model=ResetPasswordResponse, tags=["Authentication"])
def reset_password(req: ResetPasswordRequest):
    """
    Validates the 6-digit reset code and updates the user's password hash in SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, is_active FROM users WHERE email = ?
    """, (req.email.lower(),))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account registered with this email address."
        )

    if not user["is_active"]:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is deactivated. Please contact municipal administration."
        )

    # Retrieve latest reset code for this email
    cursor.execute("""
        SELECT id, reset_code, expires_at, used
        FROM password_resets
        WHERE email = ? AND reset_code = ?
        ORDER BY id DESC LIMIT 1
    """, (req.email.lower(), req.reset_code.strip()))
    entry = cursor.fetchone()

    if not entry:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please check the code and try again."
        )

    if entry["used"]:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification code has already been used. Please request a new one."
        )

    expires_at = datetime.fromisoformat(entry["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The verification code has expired. Please request a new one."
        )

    # Update password
    new_hash = hash_password(req.new_password)
    cursor.execute("""
        UPDATE users
        SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
        WHERE email = ?
    """, (new_hash, req.email.lower()))

    # Mark reset code as used
    cursor.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (entry["id"],))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="PASSWORD_RESET_SUCCESS",
        entity_type="AUTH",
        user_id=user["id"],
        user_email=user["email"],
        new_value="Password successfully reset via verified security code"
    )

    return ResetPasswordResponse(
        message="Your password has been reset successfully. You can now log in with your new password.",
        email=user["email"]
    )


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns currently authenticated user profile information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (current_user["id"],))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


@app.put("/api/auth/profile", response_model=UserResponse, tags=["Authentication"])
def update_my_profile(req: UserProfileUpdateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Allows user to update permitted personal details (Name, Phone)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    name = req.name if req.name is not None else current_user["name"]
    phone = req.phone if req.phone is not None else current_user.get("phone")

    cursor.execute("""
        UPDATE users
        SET name = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (name, phone, current_user["id"]))
    conn.commit()

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (current_user["id"],))
    updated = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="PROFILE_UPDATE",
        entity_type="USER",
        user_id=current_user["id"],
        user_email=current_user["email"],
        new_value=f"Name: {name}, Phone: {phone}"
    )

    return dict(updated)


# ==========================================
# 3. Grievance Complaints Endpoints (Role-Scoped)
# ==========================================
@app.post("/api/complaints", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED, tags=["Complaints"])
def submit_complaint(
    complaint_in: ComplaintCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Submits a structured grievance.
    Automatically binds complaint to the authenticated citizen's user_id.
    """
    try:
        created = complaint_service.create_complaint(complaint_in, citizen_id=current_user["id"])
        return created
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error: {str(e)}")


@app.get("/api/complaints", response_model=List[ComplaintResponse], tags=["Complaints"])
def list_complaints(
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Lists grievances with strict server-side scoping (Section 47 & 59):
    - CITIZEN: Returns ONLY complaints filed by current_user.
    - DEPARTMENT_OFFICER: Returns ONLY complaints assigned to the officer's department.
    - ADMIN: Returns all complaints.
    """
    return complaint_service.get_all_complaints(
        current_user=current_user,
        category=category,
        department=department,
        priority=priority,
        status=status_filter,
        search=search
    )


@app.get("/api/complaints/my", response_model=List[ComplaintResponse], tags=["Complaints"])
def list_my_complaints(
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_citizen)
):
    """
    Returns complaints filed by the authenticated citizen (Section 42).
    """
    return complaint_service.get_all_complaints(
        current_user=current_user,
        category=category,
        department=department,
        priority=priority,
        status=status_filter,
        search=search
    )


@app.get("/api/complaints/{id}", response_model=ComplaintResponse, tags=["Complaints"])
def get_complaint(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Fetches full complaint details.
    Enforces server-side resource ownership (Section 59).
    """
    try:
        complaint = complaint_service.get_complaint_by_id(id, current_user=current_user)
        if not complaint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{id}' not found.")
        return complaint
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))



@app.get("/api/admin/complaints", response_model=List[ComplaintResponse], tags=["Complaints"])
def list_admin_complaints(
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin-only: lists all municipal complaints with search and filters (Section 42).
    """
    return complaint_service.get_all_complaints(
        current_user=current_user,
        category=category,
        department=department,
        priority=priority,
        status=status_filter,
        search=search
    )


@app.get("/api/admin/complaints/{id}", response_model=ComplaintResponse, tags=["Complaints"])
def get_admin_complaint(id: str, current_user: Dict[str, Any] = Depends(require_admin)):
    """
    Admin-only: fetches single complaint details (Section 42).
    """
    complaint = complaint_service.get_complaint_by_id(id, current_user=current_user)
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{id}' not found.")
    return complaint



@app.put("/api/complaints/{id}/status", response_model=ComplaintResponse, tags=["Complaints"])
def update_status(
    id: str,
    payload: StatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """
    Updates complaint status. Allowed for DEPARTMENT_OFFICER (of assigned dept) and ADMIN.
    """
    try:
        updated = complaint_service.update_complaint_status(
            complaint_id=id,
            new_status=payload.status,
            notes=payload.notes,
            changed_by=payload.changed_by or current_user["name"],
            current_user=current_user,
            resolution_message=payload.resolution_message
        )
        return updated
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


# -------------------------------------------------------------
# 5-Stage Grievance Lifecycle Actions
# -------------------------------------------------------------

@app.put("/api/complaints/{id}/acknowledge", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def acknowledge_complaint(
    id: str,
    payload: Optional[AcknowledgeRequest] = None,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Stage 1 -> 2: Admin acknowledges newly submitted complaint (Section 74).
    """
    try:
        notes = payload.notes if payload else None
        return complaint_service.acknowledge_complaint(id, notes, current_user)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/accept", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def accept_complaint(
    id: str,
    payload: AcceptRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Stage 2 -> 3: Admin accepts complaint and transmits description to citizen (Section 75 & 76).
    """
    try:
        return complaint_service.accept_complaint(
            complaint_id=id,
            department=payload.department,
            priority=payload.priority,
            message=payload.message,
            current_user=current_user
        )
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/start-work", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def start_work(
    id: str,
    payload: Optional[StartWorkRequest] = None,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """
    Stage 3 -> 4: Admin/Officer starts work on complaint (Section 77).
    """
    try:
        msg = payload.message if payload else None
        return complaint_service.start_work(id, msg, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.post("/api/complaints/{id}/progress-update", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def add_progress_update(
    id: str,
    payload: ProgressUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """
    Progress update while IN_PROGRESS (Section 78).
    """
    try:
        return complaint_service.add_progress_update(id, payload.message, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/complete-work", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def complete_work(
    id: str,
    payload: CompleteWorkRequest,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """
    Stage 4 -> 5: Admin/Officer marks work as completed (Section 79).
    """
    try:
        return complaint_service.complete_work(id, payload.completion_message, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/inform-user", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def inform_user(
    id: str,
    payload: InformUserRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Stage 5 -> 6: Admin informs citizen of resolution (Section 80).
    """
    try:
        return complaint_service.inform_user(id, payload.notification_message, current_user)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/close", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def close_complaint(
    id: str,
    payload: Optional[CloseComplaintRequest] = None,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Stage 6 -> 7: Admin formally closes complaint (Section 81).
    """
    try:
        msg = payload.closure_message if payload else None
        return complaint_service.close_complaint(id, msg, current_user)
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


# Section 42 POST Endpoints for Grievance Lifecycle
@app.post("/api/admin/complaints/{id}/acknowledge", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_acknowledge_complaint(
    id: str,
    payload: Optional[AcknowledgeRequest] = None,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """POST alias: Admin acknowledges complaint (Section 42)."""
    return acknowledge_complaint(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/accept", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_accept_complaint(
    id: str,
    payload: AcceptRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """POST alias: Admin accepts complaint and transmits description (Section 42)."""
    return accept_complaint(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/start-work", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_start_work(
    id: str,
    payload: Optional[StartWorkRequest] = None,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """POST alias: Admin/Officer starts work (Section 42)."""
    return start_work(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/progress", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
@app.post("/api/admin/complaints/{id}/progress-update", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
@app.post("/api/complaints/{id}/progress", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_add_progress_update(
    id: str,
    payload: ProgressUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """POST alias: Admin/Officer posts progress update (Section 42)."""
    return add_progress_update(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/complete", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
@app.post("/api/admin/complaints/{id}/complete-work", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
@app.put("/api/complaints/{id}/complete", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_complete_work(
    id: str,
    payload: CompleteWorkRequest,
    current_user: Dict[str, Any] = Depends(require_officer_or_admin)
):
    """POST alias: Admin/Officer marks work complete (Section 42)."""
    return complete_work(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/inform-user", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_inform_user(
    id: str,
    payload: InformUserRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """POST alias: Admin transmits resolution to citizen (Section 42)."""
    return inform_user(id=id, payload=payload, current_user=current_user)


@app.post("/api/admin/complaints/{id}/close", response_model=ComplaintResponse, tags=["Grievance Lifecycle"])
def admin_close_complaint(
    id: str,
    payload: Optional[CloseComplaintRequest] = None,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """POST alias: Admin closes complaint (Section 42)."""
    return close_complaint(id=id, payload=payload, current_user=current_user)



@app.get("/api/complaints/{id}/timeline", response_model=List[TimelineItemResponse], tags=["Grievance Lifecycle"])
def get_complaint_timeline(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Returns full chronological timeline of all events and messages (Section 88).
    """
    try:
        return complaint_service.get_timeline(id, current_user=current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -------------------------------------------------------------
# In-App Notifications Endpoints (Section 89)
# -------------------------------------------------------------

@app.get("/api/notifications", tags=["Notifications"])
def get_user_notifications(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Fetches in-app notifications and unread count for current user."""
    return complaint_service.get_notifications(current_user["id"])


@app.put("/api/notifications/{id}/read", tags=["Notifications"])
def mark_notification_read(id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Marks single notification as read."""
    complaint_service.mark_notification_read(id, current_user["id"])
    return {"success": True}


@app.put("/api/notifications/read-all", tags=["Notifications"])
def mark_all_notifications_read(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Marks all notifications as read for current user."""
    complaint_service.mark_all_notifications_read(current_user["id"])
    return {"success": True}


@app.put("/api/admin/complaints/{id}/assign", response_model=ComplaintResponse, tags=["Admin Work Assignment"])
def accept_and_assign_complaint(
    id: str,
    payload: ComplaintAssignRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin action: Accepts a complaint, assigns it to a department, and dispatches work.
    Transitions status to 'Assigned' / 'ACCEPTED' and logs in the action tracking timeline.
    """
    try:
        updated = complaint_service.assign_department_by_admin(
            complaint_id=id,
            department=payload.department,
            priority=payload.priority,
            notes=payload.notes,
            current_user=current_user,
            admin_message=payload.admin_message
        )
        return updated
    except ValueError as e:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(e))


@app.put("/api/complaints/{id}/department", response_model=ComplaintResponse, tags=["Complaints"])
@app.put("/api/admin/complaints/{id}/override", response_model=ComplaintResponse, tags=["Complaints"])
@app.post("/api/admin/complaints/{id}/override", response_model=ComplaintResponse, tags=["Complaints"])
def manual_department_override(
    id: str,
    payload: DepartmentOverrideRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin-only manual department override.
    Preserves original AI decision and reasoning trace (Section 56).
    """
    try:
        updated = complaint_service.override_department(
            complaint_id=id,
            new_dept=payload.department,
            reason=payload.reason,
            officer_name=current_user["name"],
            current_user=current_user
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/api/complaints/{id}/reasoning", response_model=List[ReasoningTraceStepResponse], tags=["AI Reasoning"])
def get_complaint_reasoning_trace(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns reasoning trace for an authorized complaint."""
    try:
        complaint = complaint_service.get_complaint_by_id(id, current_user=current_user)
        if not complaint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Complaint '{id}' not found.")
        return complaint.get("reasoning_trace", [])
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ==========================================
# 4. Admin User Management Endpoints (Section 53)
# ==========================================
@app.get("/api/admin/users", response_model=List[UserResponse], tags=["Admin User Management"])
def list_users(
    role: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: lists all users with role and department filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE 1=1
    """
    params = []

    if role:
        query += " AND u.role = ?"
        params.append(role.upper())
    if department_id:
        query += " AND u.department_id = ?"
        params.append(department_id)
    if search:
        query += " AND (u.name LIKE ? OR u.email LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s])

    query += " ORDER BY u.id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    users = [dict(r) for r in rows]
    conn.close()
    return users


@app.post("/api/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Admin User Management"])
def create_user_by_admin(
    req: UserCreateAdminRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: creates an officer or administrator account."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (req.email.lower(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    pw_hash = hash_password(req.password)
    cursor.execute("""
        INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (req.name, req.email.lower(), req.phone, pw_hash, req.role, req.department_id if req.role == "DEPARTMENT_OFFICER" else None))

    new_id = cursor.lastrowid
    conn.commit()

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (new_id,))
    created_user = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="ADMIN_CREATE_USER",
        entity_type="USER",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=str(new_id),
        new_value=f"Role: {req.role}, Dept: {req.department_id}"
    )

    return dict(created_user)


@app.put("/api/admin/users/{id}/status", response_model=UserResponse, tags=["Admin User Management"])
def toggle_user_active_status(
    id: int,
    payload: UserStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin-only: activates or deactivates a user.
    Guards against deactivating the last active administrator!
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, email, role, is_active FROM users WHERE id = ?", (id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Guard: Prevent deactivating the last active administrator
    if target["role"] == "ADMIN" and not payload.is_active:
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND is_active = 1")
        active_admins = cursor.fetchone()[0]
        if active_admins <= 1:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Constraint Violation: Cannot deactivate the last remaining active administrator."
            )

    cursor.execute("""
        UPDATE users
        SET is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (1 if payload.is_active else 0, id))
    conn.commit()

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (id,))
    updated = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="USER_STATUS_CHANGE",
        entity_type="USER",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=str(id),
        old_value=f"Active: {bool(target['is_active'])}",
        new_value=f"Active: {payload.is_active}"
    )

    return dict(updated)


@app.put("/api/admin/users/{id}/role", response_model=UserResponse, tags=["Admin User Management"])
def change_user_role(
    id: int,
    payload: UserRoleUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin-only: modifies user role or assigns an officer to a department.
    Guards against removing the last active administrator!
    """
    new_role = payload.role.upper()
    valid_roles = {"CITIZEN", "DEPARTMENT_OFFICER", "ADMIN"}
    if new_role not in valid_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role. Must be one of: {valid_roles}")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, email, role, is_active FROM users WHERE id = ?", (id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Guard: Prevent demoting the last active administrator
    if target["role"] == "ADMIN" and new_role != "ADMIN":
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND is_active = 1")
        active_admins = cursor.fetchone()[0]
        if active_admins <= 1:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Constraint Violation: Cannot demote the last remaining active administrator."
            )

    dept_id = payload.department_id if new_role == "DEPARTMENT_OFFICER" else None
    cursor.execute("""
        UPDATE users
        SET role = ?, department_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_role, dept_id, id))
    conn.commit()

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (id,))
    updated = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="USER_ROLE_CHANGE",
        entity_type="USER",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=str(id),
        old_value=f"Role: {target['role']}",
        new_value=f"Role: {new_role}, Dept: {dept_id}"
    )

    return dict(updated)


@app.put("/api/admin/users/{id}", response_model=UserResponse, tags=["Admin User Management"])
def update_user_by_admin(
    id: int,
    payload: AdminUserUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin-only: updates user details, role, department, or active status (Section 42).
    Guards against deactivating or demoting the last active administrator!
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, role, department_id, is_active FROM users WHERE id = ?", (id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    new_role = payload.role.upper() if payload.role else target["role"]
    new_active = (1 if payload.is_active else 0) if payload.is_active is not None else target["is_active"]

    if target["role"] == "ADMIN" and (new_role != "ADMIN" or new_active == 0):
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'ADMIN' AND is_active = 1")
        active_admins = cursor.fetchone()[0]
        if active_admins <= 1:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Constraint Violation: Cannot demote or deactivate the last remaining active administrator."
            )

    new_name = payload.name if payload.name is not None else target["name"]
    new_phone = payload.phone if payload.phone is not None else target["phone"]
    new_dept = payload.department_id if new_role == "DEPARTMENT_OFFICER" else None

    cursor.execute("""
        UPDATE users
        SET name = ?, phone = ?, role = ?, department_id = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_name, new_phone, new_role, new_dept, new_active, id))
    conn.commit()

    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.role, u.department_id, u.is_active, u.created_at, u.updated_at, d.name as department_name
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.department_id
        WHERE u.id = ?
    """, (id,))
    updated = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="ADMIN_UPDATE_USER",
        entity_type="USER",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=str(id),
        new_value=f"Name: {new_name}, Role: {new_role}, Active: {bool(new_active)}"
    )

    return dict(updated)


# ==========================================
# 5. Admin Audit Log Endpoint (Section 57)
# ==========================================
@app.get("/api/admin/audit-logs", response_model=List[AuditLogResponse], tags=["Audit Logs"])
def get_system_audit_logs(
    limit: int = Query(200, le=500),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: returns structured system audit log history."""
    return audit_service.get_audit_logs(limit=limit)


# ==========================================
# 6. Admin Department Management (Section 54)
# ==========================================
@app.post("/api/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, tags=["Department Management"])
def create_department(
    dept_in: DepartmentCreateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: registers a new municipal department."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM departments WHERE department_id = ?", (dept_in.department_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department ID already exists.")

    cursor.execute("""
        INSERT INTO departments (department_id, name, description, supported_issues, escalation_authority, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dept_in.department_id,
        dept_in.name,
        dept_in.description,
        json.dumps(dept_in.supported_issues),
        dept_in.escalation_authority,
        1 if dept_in.is_active else 0
    ))
    conn.commit()

    cursor.execute("SELECT * FROM departments WHERE department_id = ?", (dept_in.department_id,))
    row = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="DEPARTMENT_CREATED",
        entity_type="DEPARTMENT",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=dept_in.department_id,
        new_value=dept_in.name
    )

    return {
        "department_id": row["department_id"],
        "name": row["name"],
        "description": row["description"],
        "supported_issues": json.loads(row["supported_issues"] or "[]"),
        "escalation_authority": row["escalation_authority"],
        "is_active": bool(row["is_active"])
    }


@app.put("/api/departments/{dept_id}", response_model=DepartmentResponse, tags=["Department Management"])
def update_department(
    dept_id: str,
    dept_in: DepartmentUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: updates department properties or soft-deactivates."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM departments WHERE department_id = ?", (dept_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")

    name = dept_in.name if dept_in.name is not None else current["name"]
    desc = dept_in.description if dept_in.description is not None else current["description"]
    issues = json.dumps(dept_in.supported_issues) if dept_in.supported_issues is not None else current["supported_issues"]
    authority = dept_in.escalation_authority if dept_in.escalation_authority is not None else current["escalation_authority"]
    is_active = (1 if dept_in.is_active else 0) if dept_in.is_active is not None else current["is_active"]

    cursor.execute("""
        UPDATE departments
        SET name = ?, description = ?, supported_issues = ?, escalation_authority = ?, is_active = ?
        WHERE department_id = ?
    """, (name, desc, issues, authority, is_active, dept_id))
    conn.commit()

    cursor.execute("SELECT * FROM departments WHERE department_id = ?", (dept_id,))
    row = cursor.fetchone()
    conn.close()

    audit_service.log_event(
        action="DEPARTMENT_UPDATED",
        entity_type="DEPARTMENT",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=dept_id,
        new_value=f"Active: {bool(is_active)}"
    )

    return {
        "department_id": row["department_id"],
        "name": row["name"],
        "description": row["description"],
        "supported_issues": json.loads(row["supported_issues"] or "[]"),
        "escalation_authority": row["escalation_authority"],
        "is_active": bool(row["is_active"])
    }


# ==========================================
# 7. Dynamic CSP Validation Endpoint
# ==========================================
@app.post("/api/validate-complaint", response_model=ValidationResultResponse, tags=["Validation & CSP"])
def validate_complaint(payload: ComplaintValidateRequest):
    is_valid, violations, warnings = validate_complaint_constraints(payload.model_dump())
    return ValidationResultResponse(
        valid=is_valid,
        violations=violations,
        warnings=warnings
    )


# ==========================================
# 8. Knowledge Base & Rules Endpoints
# ==========================================
@app.get("/api/rules", tags=["Knowledge Base & Rules"])
def get_all_rules():
    """Returns active production rules."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules ORDER BY priority_order ASC, rule_id ASC")
    rows = cursor.fetchall()
    rules = []
    for r in rows:
        rules.append({
            "rule_id": r["rule_id"],
            "rule_name": r["rule_name"],
            "rule_type": r["rule_type"],
            "description": r["description"],
            "conditions": json.loads(r["conditions_json"] or "[]"),
            "conclusion": json.loads(r["conclusion_json"] or "{}"),
            "priority_order": r["priority_order"],
            "is_active": bool(r["is_active"])
        })
    conn.close()
    return rules


@app.put("/api/rules/{rule_id}/toggle", tags=["Knowledge Base & Rules"])
def toggle_rule(rule_id: str, current_user: Dict[str, Any] = Depends(require_admin)):
    """Admin-only: enables or disables an AI production rule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_active, rule_name FROM rules WHERE rule_id = ?", (rule_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found.")

    new_state = 0 if row["is_active"] else 1
    cursor.execute("UPDATE rules SET is_active = ? WHERE rule_id = ?", (new_state, rule_id))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="RULE_TOGGLE",
        entity_type="RULE",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=rule_id,
        old_value=f"Active: {bool(row['is_active'])}",
        new_value=f"Active: {bool(new_state)}"
    )

    return {"rule_id": rule_id, "is_active": bool(new_state)}


@app.get("/api/admin/rules", tags=["Knowledge Base & Rules"])
def get_admin_rules(current_user: Dict[str, Any] = Depends(require_admin)):
    """Admin-only: lists all AI production rules (Section 42)."""
    return get_all_rules()


@app.post("/api/admin/rules", status_code=status.HTTP_201_CREATED, tags=["Knowledge Base & Rules"])
def create_admin_rule(
    payload: RuleCreateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: creates a new rule in the knowledge base (Section 42)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rules WHERE rule_id = ?", (payload.rule_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Rule ID '{payload.rule_id}' already exists.")

    cursor.execute("""
        INSERT INTO rules (rule_id, rule_name, rule_type, description, conditions_json, conclusion_json, priority_order, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.rule_id,
        payload.rule_name,
        payload.rule_type,
        payload.description,
        json.dumps(payload.conditions),
        json.dumps(payload.conclusion),
        payload.priority_order,
        1 if payload.is_active else 0
    ))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="RULE_CREATED",
        entity_type="RULE",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=payload.rule_id,
        new_value=payload.rule_name
    )

    return {"rule_id": payload.rule_id, "message": "Rule created successfully."}


@app.put("/api/admin/rules/{id}", tags=["Knowledge Base & Rules"])
def update_admin_rule(
    id: str,
    payload: RuleUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: updates an existing rule (Section 42)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules WHERE rule_id = ?", (id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule '{id}' not found.")

    name = payload.rule_name if payload.rule_name is not None else current["rule_name"]
    rtype = payload.rule_type if payload.rule_type is not None else current["rule_type"]
    desc = payload.description if payload.description is not None else current["description"]
    cond = json.dumps(payload.conditions) if payload.conditions is not None else current["conditions_json"]
    conc = json.dumps(payload.conclusion) if payload.conclusion is not None else current["conclusion_json"]
    prio = payload.priority_order if payload.priority_order is not None else current["priority_order"]
    active = (1 if payload.is_active else 0) if payload.is_active is not None else current["is_active"]

    cursor.execute("""
        UPDATE rules
        SET rule_name = ?, rule_type = ?, description = ?, conditions_json = ?, conclusion_json = ?, priority_order = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE rule_id = ?
    """, (name, rtype, desc, cond, conc, prio, active, id))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="RULE_UPDATED",
        entity_type="RULE",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=id,
        new_value=f"Active: {bool(active)}"
    )

    return {"rule_id": id, "message": "Rule updated successfully."}


@app.delete("/api/admin/rules/{id}", tags=["Knowledge Base & Rules"])
def delete_admin_rule(
    id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Admin-only: deletes an existing rule (Section 42)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rules WHERE rule_id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rule '{id}' not found.")

    cursor.execute("DELETE FROM rules WHERE rule_id = ?", (id,))
    conn.commit()
    conn.close()

    audit_service.log_event(
        action="RULE_DELETED",
        entity_type="RULE",
        user_id=current_user["id"],
        user_email=current_user["email"],
        entity_id=id
    )

    return {"rule_id": id, "message": "Rule deleted successfully."}



@app.get("/api/departments", response_model=List[DepartmentResponse], tags=["Knowledge Base & Rules"])
def get_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY name ASC")
    rows = cursor.fetchall()
    depts = []
    for r in rows:
        depts.append({
            "department_id": r["department_id"],
            "name": r["name"],
            "description": r["description"],
            "supported_issues": json.loads(r["supported_issues"] or "[]"),
            "escalation_authority": r["escalation_authority"],
            "is_active": bool(r["is_active"])
        })
    conn.close()
    return depts


@app.get("/api/categories", response_model=List[CategoryResponse], tags=["Knowledge Base & Rules"])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories ORDER BY name ASC")
    rows = cursor.fetchall()
    cats = [dict(r) for r in rows]
    conn.close()
    return cats


@app.get("/api/issue-types/{category}", response_model=List[IssueTypeResponse], tags=["Knowledge Base & Rules"])
def get_issue_types_for_category(category: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT it.* FROM issue_types it
        JOIN categories c ON it.category_id = c.category_id
        WHERE c.name = ? OR c.category_id = ?
        ORDER BY it.name ASC
    """, (category, category))
    rows = cursor.fetchall()
    issues = [dict(r) for r in rows]
    conn.close()
    return issues


@app.get("/api/municipal-zones", tags=["Chennai Civic Administration"])
def get_chennai_municipal_zones():
    """Returns the 15 Greater Chennai Corporation (GCC) zones and their 200 wards."""
    return get_all_zones()


@app.get("/api/municipal-zones/{zone_identifier}/wards", tags=["Chennai Civic Administration"])
def get_chennai_wards_for_zone_endpoint(zone_identifier: str):
    """Returns the list of wards for a specific Chennai Corporation zone."""
    wards = get_wards_for_zone(zone_identifier)
    if not wards:
        raise HTTPException(
            status_code=404,
            detail=f"Zone '{zone_identifier}' not found in Greater Chennai Corporation registry."
        )
    return wards


@app.get("/api/knowledge-base", tags=["Knowledge Base & Rules"])
def get_complete_knowledge_base():
    """Returns complete symbolic representation of the AI knowledge base."""
    return {
        "departments": DEPARTMENTS_KB,
        "taxonomy": CATEGORY_ISSUE_MAP,
        "priority_precedence_hierarchy": PRIORITY_PRECEDENCE,
        "escalation_precedence_hierarchy": ESCALATION_PRECEDENCE,
        "inference_engine_specification": {
            "type": "Data-Driven Forward Chaining with Conflict Resolution",
            "cycle_detection": True,
            "missing_data_handling": "Explicit Block (No Arbitrary Guessing)"
        }
    }


# ==========================================
# 9. Dashboard Statistics Endpoint (Role-Aware)
# ==========================================
@app.get("/api/dashboard", response_model=DashboardStatsResponse, tags=["Dashboard"])
@app.get("/api/admin/analytics", response_model=DashboardStatsResponse, tags=["Dashboard"])
def get_dashboard(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Returns dashboard metrics scoped to authenticated role (Section 42)."""
    return dashboard_service.get_dashboard_metrics(current_user=current_user)



# ==========================================
# 10. Evidence Upload Endpoint (No OCR / No Vision)
# ==========================================
@app.post("/api/evidence-upload", tags=["Evidence"])
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Accepts supporting images/PDFs.
    Explicitly DOES NOT perform OCR or image classification.
    Only stores file on disk as supporting documentation.
    """
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported evidence file format '{suffix}'. Allowed: {', '.join(allowed_exts)}"
        )

    clean_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', Path(file.filename).name)
    safe_filename = f"evidence_{uuid.uuid4().hex[:8]}_{clean_name}"
    target_path = UPLOAD_DIR / safe_filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "evidence_received": True,
        "filename": safe_filename,
        "file_size": target_path.stat().st_size,
        "verification_statement": "Evidence provided and cataloged as supporting material. No automated OCR/vision inference performed."
    }


@app.get("/api/evidence/{filename}", tags=["Evidence"])
def get_evidence(filename: str):
    """
    Serves uploaded citizen supporting evidence (photos or PDF documents).
    Available to citizens, officers, and administrators.
    """
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested evidence document was not found."
        )

    ext = file_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".pdf": "application/pdf"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=safe_name,
        content_disposition_type="inline"
    )

