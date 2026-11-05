"""
Test suite verifying the handling of inconsistent complaints.
Requirements:
1. When a complaint has an inconsistency (e.g. immediate_danger=YES and severity=LOW):
   - The complaint is accepted and saved in the database with status = 'SUBMITTED'.
   - The AI recommendation is paused with the exact validation conflict message.
   - The complaint is visible in the Admin Dashboard with validation conflict indicators.
   - Admin can acknowledge, review, override/reconcile, and dispatch the complaint.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from database import get_db_connection
from utils.security import hash_password

client = TestClient(app)

EXPECTED_CONFLICT_MSG = (
    "Validation Conflict: Immediate Danger is marked Yes, but the selected severity is Low, "
    "which violates the defined constraint. The AI recommendation has been paused and the complaint "
    "requires administrative review."
)


def get_token(email: str, password: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def test_inconsistent_complaint_submission_and_admin_review():
    # 1. Citizen submits a complaint with Immediate Danger = YES and Severity = LOW
    citizen_token = get_token("priya@gmail.com", "123456")
    admin_token = get_token("admin@gmail.com", "123456")

    payload = {
        "citizen_name": "Inconsistency Test Citizen",
        "phone": "+91 98765 12345",
        "email": "priya@gmail.com",
        "ward": "Ward 101 - Anna Nagar East",
        "location": "Near Anna Arch",
        "category": "Public Lighting",
        "issue_type": "Streetlight Not Working",
        "duration_days": 1,
        "severity": "LOW",
        "immediate_danger": "YES",
        "affected_people": 15,
        "description": "Streetlight pole sparked with sparking wires near sidewalk.",
        "frequency": "OCCASIONAL",
        "safety_risk": "LOW",
        "emergency": False
    }

    res = client.post(
        "/api/complaints",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"}
    )

    assert res.status_code == 201, f"Expected 201 Created but got {res.status_code}: {res.text}"
    data = res.json()
    complaint_id = data["complaint_id"]
    assert data["status"] == "SUBMITTED"
    assert data["explanation"] == EXPECTED_CONFLICT_MSG
    assert data["escalation"] == "ADMIN_REVIEW_REQUIRED"
    assert len(data["conflicts"]) > 0

    # 2. Verify complaint appears in Admin's complaints list
    admin_res = client.get(
        "/api/complaints",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_res.status_code == 200
    complaints = admin_res.json()
    found = [c for c in complaints if c["complaint_id"] == complaint_id]
    assert len(found) == 1, f"Complaint {complaint_id} not found in admin complaints list"
    admin_comp = found[0]
    assert admin_comp["status"] == "SUBMITTED"
    assert "Validation Conflict" in admin_comp["explanation"]

    # 3. Admin acknowledges the complaint (Stage 1 -> 2)
    ack_res = client.post(
        f"/api/admin/complaints/{complaint_id}/acknowledge",
        json={"notes": "Acknowledged inconsistent complaint for administrative reconciliation."},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # 4. Admin reconciles and accepts the complaint (Stage 2 -> 3)
    accept_res = client.put(
        f"/api/complaints/{complaint_id}/accept",
        json={
            "department": "Public Lighting",
            "priority": "HIGH",
            "message": "Administrative review completed. Corrected priority to HIGH based on sparking wire risk."
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert accept_res.status_code == 200
    accepted_comp = accept_res.json()
    assert accepted_comp["status"] == "ACCEPTED"
    assert accepted_comp["department"] == "Public Lighting"
    assert accepted_comp["priority"] == "HIGH"
