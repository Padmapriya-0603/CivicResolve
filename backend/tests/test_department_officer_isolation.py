"""
Test Suite: Multi-Department Officer Isolation & Role-Based Access Control (RBAC).
Verifies that:
1. Each of the 5 department officers can log in successfully.
2. Each department officer can access ONLY the grievances assigned to their department.
3. Cross-department access attempts (GET complaint details, start work, progress updates, complete work)
   are strictly denied with HTTP 403 Forbidden.
4. Administrators retain global supervisory access across all departmental complaints.
"""

import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app
from seed_data import seed_database
from database import get_db_connection


@pytest.fixture(scope="module", autouse=True)
def setup_clean_db():
    """Initializes and seeds fresh users and clears all complaints."""
    seed_database(clean_complaints=True)


@pytest.fixture
def client():
    return TestClient(app)


def get_token(client: TestClient, email: str, password: str = "123456") -> str:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    return resp.json()["access_token"]


def create_complaint(client: TestClient, citizen_token: str, payload: dict) -> dict:
    resp = client.post(
        "/api/complaints",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"}
    )
    assert resp.status_code == 201, f"Failed to create complaint: {resp.text}"
    return resp.json()


def test_officer_logins_and_department_bindings(client):
    """Verifies that all 5 department officers authenticate and are bound to their respective departments."""
    officers = [
        ("officer.roads@gmail.com", "Road Maintenance"),
        ("officer@gmail.com", "Road Maintenance"),
        ("officer.water@gmail.com", "Water Supply"),
        ("officer.sanitation@gmail.com", "Sanitation"),
        ("officer.lighting@gmail.com", "Public Lighting"),
        ("officer.drainage@gmail.com", "Drainage")
    ]
    for email, expected_dept in officers:
        resp = client.post("/api/auth/login", json={"email": email, "password": "123456"})
        assert resp.status_code == 200, f"Login failed for {email}"
        data = resp.json()
        assert data["role"] == "DEPARTMENT_OFFICER"
        assert data["department_name"] == expected_dept


def test_department_officer_complaint_isolation(client):
    """
    Submits 5 distinct departmental complaints, then proves that each department officer
    only receives their department's tickets in the complaints list and gets 403 on others.
    """
    citizen_token = get_token(client, "priya@gmail.com")
    admin_token = get_token(client, "admin@gmail.com")

    # 1. Submit 5 complaints, one for each department
    comp_roads = create_complaint(client, citizen_token, {
        "citizen_name": "Priya",
        "phone": "9876543210",
        "email": "priya@gmail.com",
        "ward": "Ward 1",
        "location": "Main Highway",
        "category": "Roads",
        "issue_type": "Pothole",
        "severity": "MEDIUM",
        "immediate_danger": "NO",
        "safety_risk": "LOW",
        "affected_people": 10,
        "frequency": "OCCASIONAL",
        "duration_days": 2,
        "recurrence": False,
        "emergency": False,
        "description": "Pothole on main lane"
    })
    assert comp_roads["department"] == "Road Maintenance"

    comp_water = create_complaint(client, citizen_token, {
        "citizen_name": "Priya",
        "phone": "9876543210",
        "email": "priya@gmail.com",
        "ward": "Ward 2",
        "location": "North Supply Lane",
        "category": "Water",
        "issue_type": "Pipeline Leakage",
        "severity": "HIGH",
        "immediate_danger": "NO",
        "safety_risk": "HIGH",
        "affected_people": 25,
        "frequency": "CONTINUOUS",
        "duration_days": 1,
        "recurrence": False,
        "emergency": False,
        "description": "Underground pipe leaking clean water"
    })
    assert comp_water["department"] == "Water Supply"

    comp_sanitation = create_complaint(client, citizen_token, {
        "citizen_name": "Priya",
        "phone": "9876543210",
        "email": "priya@gmail.com",
        "ward": "Ward 3",
        "location": "Central Market",
        "category": "Sanitation",
        "issue_type": "Garbage Not Collected",
        "severity": "MEDIUM",
        "immediate_danger": "NO",
        "safety_risk": "LOW",
        "affected_people": 40,
        "frequency": "FREQUENT",
        "duration_days": 3,
        "recurrence": False,
        "emergency": False,
        "description": "Garbage bins overflowing near fruit market"
    })
    assert comp_sanitation["department"] == "Sanitation"

    comp_lighting = create_complaint(client, citizen_token, {
        "citizen_name": "Priya",
        "phone": "9876543210",
        "email": "priya@gmail.com",
        "ward": "Ward 4",
        "location": "South Circle",
        "category": "Public Lighting",
        "issue_type": "Streetlight Damaged",
        "severity": "LOW",
        "immediate_danger": "NO",
        "safety_risk": "NONE",
        "affected_people": 5,
        "frequency": "ONE_TIME",
        "duration_days": 1,
        "recurrence": False,
        "emergency": False,
        "description": "Lamp fixture broken on pole #12"
    })
    assert comp_lighting["department"] == "Public Lighting"

    comp_drainage = create_complaint(client, citizen_token, {
        "citizen_name": "Priya",
        "phone": "9876543210",
        "email": "priya@gmail.com",
        "ward": "Ward 5",
        "location": "Canal Embankment",
        "category": "Drainage",
        "issue_type": "Drain Blockage",
        "severity": "HIGH",
        "immediate_danger": "NO",
        "safety_risk": "MEDIUM",
        "affected_people": 15,
        "frequency": "OCCASIONAL",
        "duration_days": 2,
        "recurrence": False,
        "emergency": False,
        "description": "Storm drain clogged with silt"
    })
    assert comp_drainage["department"] == "Drainage"

    # 2. Check Administrator visibility: Sees all 5 complaints
    admin_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert len(admin_list) >= 5

    # 3. Check Road Officer visibility
    roads_token = get_token(client, "officer.roads@gmail.com")
    roads_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {roads_token}"}).json()
    assert len(roads_list) == 1
    assert roads_list[0]["complaint_id"] == comp_roads["complaint_id"]
    assert roads_list[0]["department"] == "Road Maintenance"

    # 4. Check Water Officer visibility
    water_token = get_token(client, "officer.water@gmail.com")
    water_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {water_token}"}).json()
    assert len(water_list) == 1
    assert water_list[0]["complaint_id"] == comp_water["complaint_id"]
    assert water_list[0]["department"] == "Water Supply"

    # 5. Check Sanitation Officer visibility
    sanitation_token = get_token(client, "officer.sanitation@gmail.com")
    sanitation_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {sanitation_token}"}).json()
    assert len(sanitation_list) == 1
    assert sanitation_list[0]["complaint_id"] == comp_sanitation["complaint_id"]
    assert sanitation_list[0]["department"] == "Sanitation"

    # 6. Check Public Lighting Officer visibility
    lighting_token = get_token(client, "officer.lighting@gmail.com")
    lighting_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {lighting_token}"}).json()
    assert len(lighting_list) == 1
    assert lighting_list[0]["complaint_id"] == comp_lighting["complaint_id"]
    assert lighting_list[0]["department"] == "Public Lighting"

    # 7. Check Drainage Officer visibility
    drainage_token = get_token(client, "officer.drainage@gmail.com")
    drainage_list = client.get("/api/complaints", headers={"Authorization": f"Bearer {drainage_token}"}).json()
    assert len(drainage_list) == 1
    assert drainage_list[0]["complaint_id"] == comp_drainage["complaint_id"]
    assert drainage_list[0]["department"] == "Drainage"

    # 8. Cross-Department Access Restrictions (GET details should return 403 Forbidden)
    # Water Officer attempting to access Roads complaint
    cross_get = client.get(
        f"/api/complaints/{comp_roads['complaint_id']}",
        headers={"Authorization": f"Bearer {water_token}"}
    )
    assert cross_get.status_code == 403
    assert "Access Denied" in cross_get.json()["detail"]

    # Sanitation Officer attempting to access Water complaint
    cross_get_2 = client.get(
        f"/api/complaints/{comp_water['complaint_id']}",
        headers={"Authorization": f"Bearer {sanitation_token}"}
    )
    assert cross_get_2.status_code == 403
    assert "Access Denied" in cross_get_2.json()["detail"]

    # Roads Officer attempting to access Drainage complaint
    cross_get_3 = client.get(
        f"/api/complaints/{comp_drainage['complaint_id']}",
        headers={"Authorization": f"Bearer {roads_token}"}
    )
    assert cross_get_3.status_code == 403
    assert "Access Denied" in cross_get_3.json()["detail"]

    # 9. Cross-Department Action Restrictions (Start Work, Progress Update, Complete Work)
    # Admin acknowledges Roads complaint first so it can progress
    client.post(
        f"/api/admin/complaints/{comp_roads['complaint_id']}/acknowledge",
        json={"notes": "Acknowledged by admin."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        f"/api/admin/complaints/{comp_roads['complaint_id']}/accept",
        json={"message": "Accepted for action."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Water Officer attempts to START WORK on Roads complaint -> 403 Forbidden
    cross_action = client.put(
        f"/api/complaints/{comp_roads['complaint_id']}/start-work",
        json={"message": "Water team attempting unauthorized road work"},
        headers={"Authorization": f"Bearer {water_token}"}
    )
    assert cross_action.status_code == 403
    assert "Access Denied" in cross_action.json()["detail"]

    # Legitimate Roads Officer starts work on their own complaint -> 200 OK
    valid_action = client.put(
        f"/api/complaints/{comp_roads['complaint_id']}/start-work",
        json={"message": "Roads maintenance crew dispatched to inspect pothole."},
        headers={"Authorization": f"Bearer {roads_token}"}
    )
    assert valid_action.status_code == 200
    assert valid_action.json()["status"] == "IN_PROGRESS"

    # Drainage Officer attempts to POST PROGRESS UPDATE on Roads complaint -> 403 Forbidden
    cross_progress = client.post(
        f"/api/complaints/{comp_roads['complaint_id']}/progress-update",
        json={"message": "Drainage team update"},
        headers={"Authorization": f"Bearer {drainage_token}"}
    )
    assert cross_progress.status_code == 403
    assert "Access Denied" in cross_progress.json()["detail"]

    # Legitimate Roads Officer posts progress update -> 200 OK
    valid_progress = client.post(
        f"/api/complaints/{comp_roads['complaint_id']}/progress-update",
        json={"message": "Asphalt patch applied; awaiting curing."},
        headers={"Authorization": f"Bearer {roads_token}"}
    )
    assert valid_progress.status_code == 200

    # Lighting Officer attempts to COMPLETE WORK on Roads complaint -> 403 Forbidden
    cross_complete = client.put(
        f"/api/complaints/{comp_roads['complaint_id']}/complete-work",
        json={"completion_message": "Lighting team completing road"},
        headers={"Authorization": f"Bearer {lighting_token}"}
    )
    assert cross_complete.status_code == 403
    assert "Access Denied" in cross_complete.json()["detail"]

    # Legitimate Roads Officer completes work -> 200 OK
    valid_complete = client.put(
        f"/api/complaints/{comp_roads['complaint_id']}/complete-work",
        json={"completion_message": "Pothole repair successfully completed and road cleared."},
        headers={"Authorization": f"Bearer {roads_token}"}
    )
    assert valid_complete.status_code == 200
    assert valid_complete.json()["status"] == "WORK_COMPLETED"
