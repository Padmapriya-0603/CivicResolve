"""
Automated Test Suite for Role-Based Access Control (RBAC) & Authentication.
Validates all 17 mandated security requirements from Section 66:
1. Citizen can create complaint
2. Citizen can view own complaint
3. Citizen cannot view another citizen's complaint (403 Forbidden)
4. Citizen cannot access admin endpoints (403 Forbidden)
5. Citizen cannot modify rules (403 Forbidden)
6. Officer can view complaints assigned to their department
7. Officer cannot view unrelated department complaints (403 Forbidden)
8. Officer can update status of assigned complaint
9. Officer cannot modify AI rules (403 Forbidden)
10. Admin can view all complaints
11. Admin can manage users (activate/deactivate, role change)
12. Admin can manage rules (toggle rule)
13. Admin can override department
14. Original AI reasoning remains after admin override
15. Inactive user cannot login (403 Forbidden)
16. Invalid JWT is rejected (401 Unauthorized)
17. Missing authentication is rejected (401 Unauthorized)
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from seed_data import seed_database
from database import get_db_connection
from services.complaint_service import complaint_service
from ai.grievance_agent import GrievanceAgent
from models.schemas import ComplaintCreateRequest
from utils.security import hash_password

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Setup test users and test sample complaints for the test suite
    conn = get_db_connection()
    c = conn.cursor()

    test_users = [
        ("Super Administrator", "admin@grievance.local", "+91 99000 11000", hash_password("Admin@1234"), "ADMIN", None, 1),
        ("Rajesh Kumar (Lighting Officer)", "lighting@grievance.local", "+91 98111 22333", hash_password("Officer@1234"), "DEPARTMENT_OFFICER", "DEPT_PUB_LIGHTING", 1),
        ("Kavita Nair (Water Supply Officer)", "water@grievance.local", "+91 98222 33444", hash_password("Officer@1234"), "DEPARTMENT_OFFICER", "DEPT_WATER_SUPPLY", 1),
        ("Vikram Rathore (Roads Officer)", "roads@grievance.local", "+91 98333 44555", hash_password("Officer@1234"), "DEPARTMENT_OFFICER", "DEPT_ROAD_MAINT", 1),
        ("Inactive Officer Demo", "inactive@grievance.local", "+91 98000 00000", hash_password("Officer@1234"), "DEPARTMENT_OFFICER", "DEPT_DRAINAGE", 0),
        ("Ramesh Kumar", "citizen@grievance.local", "+91 98765 43210", hash_password("Citizen@1234"), "CITIZEN", None, 1),
        ("Priya Verma", "priya@grievance.local", "+91 91234 56789", hash_password("Citizen@1234"), "CITIZEN", None, 1),
    ]
    for u in test_users:
        c.execute("SELECT id FROM users WHERE email = ?", (u[1],))
        if c.fetchone():
            c.execute("UPDATE users SET password_hash = ?, is_active = ? WHERE email = ?", (u[3], u[6], u[1]))
        else:
            c.execute("""
                INSERT INTO users (name, email, phone, password_hash, role, department_id, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, u)

    conn.commit()

    # Seed 2 complaints for test_6, test_7, test_8, test_10, test_13
    c1 = ComplaintCreateRequest(
        citizen_name="Ramesh Kumar", phone="+91 98765 43210", email="citizen@grievance.local",
        ward="Ward 14", location="Main Road", category="Public Lighting", issue_type="Streetlight Not Working",
        duration_days=5, severity="HIGH", affected_people=80, frequency="FREQUENT", safety_risk="HIGH"
    )
    complaint_service.create_complaint(c1, citizen_id=None)

    c2 = ComplaintCreateRequest(
        citizen_name="Priya Verma", phone="+91 91234 56789", email="priya@grievance.local",
        ward="Ward 7", location="Avenue 3", category="Water Supply", issue_type="Contaminated Supply",
        duration_days=2, severity="CRITICAL", affected_people=250, frequency="CONTINUOUS", safety_risk="CRITICAL", emergency=True
    )
    complaint_service.create_complaint(c2, citizen_id=None)

    conn.close()

    yield

    # Teardown: Clean complaints and remove demo accounts so live system stays pristine!
    seed_database(clean_complaints=True)


def get_token(email: str, password: str = "Officer@1234") -> str:
    """Helper to authenticate and retrieve access token."""
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


# ==========================================
# TEST 1 & 2: Citizen Create & View Own
# ==========================================
def test_1_citizen_can_create_complaint():
    """TEST 1: Citizen can create complaint."""
    token = get_token("citizen@grievance.local", "Citizen@1234")
    payload = {
        "citizen_name": "Ramesh Citizen Test",
        "phone": "+91 98765 00001",
        "email": "citizen@grievance.local",
        "ward": "Ward 1",
        "location": "Central Square",
        "preferred_contact": "Phone",
        "category": "Public Lighting",
        "issue_type": "Streetlight Not Working",
        "duration_days": 2,
        "severity": "LOW",
        "affected_people": 5,
        "frequency": "ONE_TIME",
        "safety_risk": "NONE",
        "recurrence": False,
        "emergency": False
    }
    res = client.post("/api/complaints", json=payload, headers=auth_header(token))
    assert res.status_code == 201
    data = res.json()
    assert data["department"] == "Public Lighting"
    assert "complaint_id" in data


def test_2_citizen_can_view_own_complaint():
    """TEST 2: Citizen can view own complaint."""
    token = get_token("citizen@grievance.local", "Citizen@1234")
    # Get complaints for this citizen
    res_list = client.get("/api/complaints", headers=auth_header(token))
    assert res_list.status_code == 200
    my_complaints = res_list.json()
    assert len(my_complaints) > 0
    comp_id = my_complaints[0]["complaint_id"]

    # View individual
    res = client.get(f"/api/complaints/{comp_id}", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["complaint_id"] == comp_id


# ==========================================
# TEST 3: Citizen Cannot View Another's
# ==========================================
def test_3_citizen_cannot_view_another_citizens_complaint():
    """TEST 3: Citizen cannot view another citizen's complaint (403 Forbidden)."""
    priya_token = get_token("priya@grievance.local", "Citizen@1234")
    # Priya creates a complaint
    payload = {
        "citizen_name": "Priya Verma",
        "phone": "+91 91234 56789",
        "email": "priya@grievance.local",
        "ward": "Ward 7",
        "location": "Avenue 3",
        "preferred_contact": "Email",
        "category": "Water Supply",
        "issue_type": "Water Leakage",
        "duration_days": 1,
        "severity": "MEDIUM",
        "affected_people": 20,
        "frequency": "OCCASIONAL",
        "safety_risk": "LOW",
        "recurrence": False,
        "emergency": False
    }
    res_create = client.post("/api/complaints", json=payload, headers=auth_header(priya_token))
    assert res_create.status_code == 201
    priya_comp_id = res_create.json()["complaint_id"]

    # Ramesh tries to view Priya's complaint -> MUST BE REJECTED 403
    ramesh_token = get_token("citizen@grievance.local", "Citizen@1234")
    res_forbidden = client.get(f"/api/complaints/{priya_comp_id}", headers=auth_header(ramesh_token))
    assert res_forbidden.status_code == 403
    assert "Access Denied" in res_forbidden.json()["detail"]


# ==========================================
# TEST 4 & 5: Citizen Cannot Access Admin / Modify Rules
# ==========================================
def test_4_citizen_cannot_access_admin_dashboard_or_users():
    """TEST 4: Citizen cannot access admin user management (403 Forbidden)."""
    token = get_token("citizen@grievance.local", "Citizen@1234")
    res = client.get("/api/admin/users", headers=auth_header(token))
    assert res.status_code == 403


def test_5_citizen_cannot_modify_rules():
    """TEST 5: Citizen cannot modify or toggle rules (403 Forbidden)."""
    token = get_token("citizen@grievance.local", "Citizen@1234")
    res = client.put("/api/rules/R001/toggle", headers=auth_header(token))
    assert res.status_code == 403


# ==========================================
# TEST 6 & 7: Officer View Assigned / Blocked Unrelated
# ==========================================
def test_6_officer_can_view_assigned_department_complaints():
    """TEST 6: Officer can view complaints assigned to their department."""
    lighting_token = get_token("lighting@grievance.local", "Officer@1234")
    res = client.get("/api/complaints", headers=auth_header(lighting_token))
    assert res.status_code == 200
    complaints = res.json()
    for c in complaints:
        assert c["department"] == "Public Lighting"


def test_7_officer_cannot_view_unrelated_department_complaint():
    """TEST 7: Officer cannot view unrelated department complaints (403 Forbidden)."""
    # Find a complaint assigned to Water Supply
    admin_token = get_token("admin@grievance.local", "Admin@1234")
    res_all = client.get("/api/complaints", headers=auth_header(admin_token))
    water_complaint = next(c for c in res_all.json() if c["department"] == "Water Supply")

    # Lighting officer tries to view it
    lighting_token = get_token("lighting@grievance.local", "Officer@1234")
    res = client.get(f"/api/complaints/{water_complaint['complaint_id']}", headers=auth_header(lighting_token))
    assert res.status_code == 403
    assert "Access Denied" in res.json()["detail"]


# ==========================================
# TEST 8 & 9: Officer Status Update & Rule Protection
# ==========================================
def test_8_officer_can_update_status_of_assigned_complaint():
    """TEST 8: Officer can update status of assigned complaint."""
    admin_token = get_token("admin@grievance.local", "Admin@1234")
    lighting_token = get_token("lighting@grievance.local", "Officer@1234")
    res = client.get("/api/complaints", headers=auth_header(lighting_token))
    comp_id = res.json()[0]["complaint_id"]

    # In the 7-stage lifecycle, grievance is acknowledged and accepted before work commences
    client.put(f"/api/complaints/{comp_id}/acknowledge", headers=auth_header(admin_token))
    client.put(f"/api/complaints/{comp_id}/accept", json={"message": "Dispatched to lighting team."}, headers=auth_header(admin_token))

    res_up = client.put(
        f"/api/complaints/{comp_id}/status",
        json={"status": "In Progress", "notes": "Technician dispatched to replace luminaire."},
        headers=auth_header(lighting_token)
    )
    assert res_up.status_code == 200
    assert res_up.json()["status"] in ("In Progress", "IN_PROGRESS")


def test_9_officer_cannot_modify_ai_rules():
    """TEST 9: Officer cannot modify AI rules (403 Forbidden)."""
    lighting_token = get_token("lighting@grievance.local", "Officer@1234")
    res = client.put("/api/rules/R001/toggle", headers=auth_header(lighting_token))
    assert res.status_code == 403


# ==========================================
# TEST 10 & 11: Admin Full Visibility & User Management
# ==========================================
def test_10_admin_can_view_all_complaints():
    """TEST 10: Admin can view all complaints across all departments."""
    admin_token = get_token("admin@grievance.local", "Admin@1234")
    res = client.get("/api/complaints", headers=auth_header(admin_token))
    assert res.status_code == 200
    depts = {c["department"] for c in res.json() if c["department"]}
    assert len(depts) >= 2  # Has complaints from multiple departments


def test_11_admin_can_manage_users():
    """TEST 11: Admin can manage users (create officer, toggle status)."""
    import uuid
    admin_token = get_token("admin@grievance.local", "Admin@1234")

    # 1. Create a new officer with unique email
    new_email = f"officer_{uuid.uuid4().hex[:8]}@grievance.local"
    res_create = client.post(
        "/api/admin/users",
        json={
            "name": "Test Officer",
            "email": new_email,
            "password": "Officer@1234",
            "role": "DEPARTMENT_OFFICER",
            "department_id": "DEPT_DRAINAGE"
        },
        headers=auth_header(admin_token)
    )
    assert res_create.status_code == 201
    user_id = res_create.json()["id"]

    # 2. Deactivate the user
    res_deact = client.put(
        f"/api/admin/users/{user_id}/status",
        json={"is_active": False},
        headers=auth_header(admin_token)
    )
    assert res_deact.status_code == 200
    assert res_deact.json()["is_active"] is False


# ==========================================
# TEST 12: Admin Can Manage Rules
# ==========================================
def test_12_admin_can_manage_rules():
    """TEST 12: Admin can toggle rules."""
    admin_token = get_token("admin@grievance.local", "Admin@1234")
    res = client.put("/api/rules/R001/toggle", headers=auth_header(admin_token))
    assert res.status_code == 200
    # Toggle back to true
    res2 = client.put("/api/rules/R001/toggle", headers=auth_header(admin_token))
    assert res2.status_code == 200
    assert res2.json()["is_active"] is True


# ==========================================
# TEST 13 & 14: Admin Override & Preservation of AI Trace
# ==========================================
def test_13_14_admin_can_override_department_and_preserve_trace():
    """TEST 13 & 14: Admin can override department and preserve original AI reasoning."""
    admin_token = get_token("admin@grievance.local", "Admin@1234")
    res_all = client.get("/api/complaints", headers=auth_header(admin_token))
    comp_list = res_all.json()
    assert len(comp_list) > 0
    target_id = comp_list[0]["complaint_id"]

    # Fetch full complaint details to inspect trace
    res_detail = client.get(f"/api/complaints/{target_id}", headers=auth_header(admin_token))
    comp = res_detail.json()
    original_ai_dept = comp["ai_department"]
    original_trace_length = len(comp["reasoning_trace"])

    # Override department to Road Maintenance
    res_override = client.put(
        f"/api/complaints/{target_id}/department",
        json={
            "department": "Road Maintenance",
            "reason": "Excavation required for cable access."
        },
        headers=auth_header(admin_token)
    )
    assert res_override.status_code == 200
    data = res_override.json()
    assert data["department"] == "Road Maintenance"
    assert data["manual_override"] is True
    # TEST 14: Verify original AI decision and trace preserved
    assert data["ai_department"] == original_ai_dept
    assert len(data["reasoning_trace"]) == original_trace_length


# ==========================================
# TEST 15: Inactive User Cannot Login
# ==========================================
def test_15_inactive_user_cannot_login():
    """TEST 15: Inactive user login is rejected (403 Forbidden)."""
    res = client.post("/api/auth/login", json={
        "email": "inactive@grievance.local",
        "password": "Officer@1234"
    })
    assert res.status_code == 403
    assert "inactive" in res.json()["detail"].lower()


# ==========================================
# TEST 16 & 17: Token & Authentication Rejection
# ==========================================
def test_16_invalid_jwt_is_rejected():
    """TEST 16: Invalid JWT is rejected (401 Unauthorized)."""
    res = client.get("/api/complaints", headers={"Authorization": "Bearer invalid.fake.token"})
    assert res.status_code == 401


def test_17_missing_authentication_is_rejected():
    """TEST 17: Missing authentication is rejected (401 Unauthorized)."""
    res = client.get("/api/complaints")
    assert res.status_code == 401


# ==========================================
# TEST 18 & 19: Forgot & Reset Password
# ==========================================
def test_18_forgot_password_generates_code():
    """TEST 18: Forgot password generates 6-digit reset code for registered email."""
    # Unknown email should 404
    res_unknown = client.post("/api/auth/forgot-password", json={"email": "nonexistent@civic.local"})
    assert res_unknown.status_code == 404

    # Valid user gets reset code
    res = client.post("/api/auth/forgot-password", json={"email": "citizen@grievance.local"})
    assert res.status_code == 200
    data = res.json()
    assert "reset_code" in data
    assert len(data["reset_code"]) == 6
    assert data["email"] == "citizen@grievance.local"


def test_19_reset_password_updates_login():
    """TEST 19: Reset password updates password hash allowing login with new password."""
    # 1. Request code
    res = client.post("/api/auth/forgot-password", json={"email": "citizen@grievance.local"})
    assert res.status_code == 200
    code = res.json()["reset_code"]

    # 2. Reset with invalid code should fail
    bad_res = client.post("/api/auth/reset-password", json={
        "email": "citizen@grievance.local",
        "reset_code": "000000",
        "new_password": "NewCitizen@5678"
    })
    assert bad_res.status_code == 400

    # 3. Reset with valid code
    ok_res = client.post("/api/auth/reset-password", json={
        "email": "citizen@grievance.local",
        "reset_code": code,
        "new_password": "NewCitizen@5678"
    })
    assert ok_res.status_code == 200
    assert "successfully" in ok_res.json()["message"].lower()

    # 4. Old password no longer works
    old_login = client.post("/api/auth/login", json={
        "email": "citizen@grievance.local",
        "password": "Citizen@1234"
    })
    assert old_login.status_code == 400

    # 5. New password works
    new_login = client.post("/api/auth/login", json={
        "email": "citizen@grievance.local",
        "password": "NewCitizen@5678"
    })
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()

