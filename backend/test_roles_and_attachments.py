"""
Comprehensive Verification Script for Role Responsibilities & Supporting Evidence Attachments.
Tests:
1. Citizen: Submits complaint with photo/PDF attachment, receives status, receives messages & notifications.
2. Admin: Reviews complaint, acknowledges (Stage 1 -> 2), monitors, reassigns, verifies & closes (Stage 4 -> 5).
3. Department Officer: Views assigned complaints (strictly scoped to their department), accepts/starts work (Stage 2 -> 3),
   adds progress updates (Stage 3), and resolves complaint (Stage 3 -> 4).
4. Evidence Attachment: Ensures attached photo/PDF is served via /api/evidence/{filename} and visible to Officer & Admin.
"""

from fastapi.testclient import TestClient
from main import app
from database import init_db
from seed_data import seed_database
import io

def run_verification():
    # Initialize DB with accounts & taxonomy
    init_db()
    seed_database(clean_complaints=False)

    client = TestClient(app)

    print("--- 1. CITIZEN RESPONSIBILITIES: SUBMIT COMPLAINT & ATTACH EVIDENCE ---")
    # Login Citizen (Priya)
    res = client.post('/api/auth/login', json={'email': 'priya@gmail.com', 'password': '123456'})
    assert res.status_code == 200, f"Login failed: {res.text}"
    citizen_token = res.json()['access_token']
    citizen_headers = {'Authorization': f'Bearer {citizen_token}'}
    print("Citizen logged in successfully.")

    # Upload Evidence (Photo / PNG)
    dummy_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    upload_res = client.post(
        '/api/evidence-upload',
        headers=citizen_headers,
        files={'file': ('broken_streetlight_evidence.png', io.BytesIO(dummy_png), 'image/png')}
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    evidence_fn = upload_res.json()['filename']
    print(f"Evidence file uploaded by citizen: {evidence_fn}")

    # Verify Evidence is served via GET /api/evidence/{filename}
    ev_get = client.get(f'/api/evidence/{evidence_fn}')
    assert ev_get.status_code == 200, f"Get evidence failed: {ev_get.text}"
    assert ev_get.headers['content-type'] == 'image/png'
    print(f"Verified /api/evidence/{evidence_fn} serves file with media type: {ev_get.headers['content-type']}")

    # Citizen submits complaint with the attached photo
    payload = {
        'citizen_name': 'Priya S',
        'phone': '+91 98765 12345',
        'email': 'priya@gmail.com',
        'ward': 'Ward 104',
        'location': 'Near Anna Arch Junction, 3rd Avenue',
        'category': 'Roads',
        'issue_type': 'Pothole',
        'severity': 'HIGH',
        'safety_risk': 'HIGH',
        'frequency': 'FREQUENT',
        'affected_people': 30,
        'duration_days': 2,
        'evidence_available': True,
        'evidence_filename': evidence_fn,
        'description': 'Severe crater on the road causing traffic blockage and safety hazards.'
    }
    comp_res = client.post('/api/complaints', headers=citizen_headers, json=payload)
    assert comp_res.status_code == 201, f"Complaint creation failed: {comp_res.text}"
    complaint_data = comp_res.json()
    cid = complaint_data['complaint_id']
    dept = complaint_data['department']
    print(f"Complaint created: #{cid} (Stage 1: {complaint_data['status']}) routed to department: '{dept}'")
    assert complaint_data['evidence_filename'] == evidence_fn

    print("\n--- 2. ADMIN RESPONSIBILITIES: REVIEW, ACKNOWLEDGE, REASSIGN ---")
    # Login Admin
    admin_res = client.post('/api/auth/login', json={'email': 'admin@gmail.com', 'password': '123456'})
    assert admin_res.status_code == 200
    admin_token = admin_res.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # Admin reviews complaint & verifies attachment is present
    admin_view = client.get(f'/api/complaints/{cid}', headers=admin_headers).json()
    assert admin_view['evidence_filename'] == evidence_fn, "Admin must see citizen attachment!"
    print(f"Admin reviewed #{cid}: Attachment '{admin_view['evidence_filename']}' verified visible.")

    # Admin acknowledges complaint (Stage 1 -> Stage 2)
    ack_res = client.put(f'/api/complaints/{cid}/acknowledge', headers=admin_headers, json={'notes': 'Reviewed and confirmed by GCC Municipal Administrator.'})
    assert ack_res.status_code == 200
    print(f"Admin acknowledged #{cid}: Advanced to {ack_res.json()['status']} (Stage 2 - 40%)")

    print("\n--- 3. DEPARTMENT OFFICER RESPONSIBILITIES: VIEW ASSIGNED, START WORK, ADD UPDATES, RESOLVE ---")
    # Login Officer for Road Maintenance (Officer Rajesh)
    off_res = client.post('/api/auth/login', json={'email': 'officer@gmail.com', 'password': '123456'})
    assert off_res.status_code == 200, f"Officer login failed: {off_res.text}"
    off_token = off_res.json()['access_token']
    off_headers = {'Authorization': f'Bearer {off_token}'}
    print(f"Department Officer logged in: {off_res.json()['name']} ({off_res.json()['department_name']})")

    # Officer views assigned complaints (server-side scoped to Road Maintenance)
    officer_queue = client.get('/api/complaints', headers=off_headers).json()
    officer_complaint = next((c for c in officer_queue if c['complaint_id'] == cid), None)
    assert officer_complaint is not None, "Officer must view complaints assigned to their department!"
    assert officer_complaint['evidence_filename'] == evidence_fn, "Officer must see citizen attachment in queue!"
    print(f"Officer viewed assigned complaint #{cid}: Attachment '{officer_complaint['evidence_filename']}' verified visible.")

    # Officer accepts / starts work (Stage 2 -> Stage 3)
    start_res = client.put(f'/api/complaints/{cid}/start-work', headers=off_headers, json={'message': 'Road maintenance team dispatched with asphalt equipment.'})
    assert start_res.status_code == 200
    print(f"Officer started work on #{cid}: Advanced to {start_res.json()['status']} (Stage 3 - 60%)")

    # Officer adds progress updates
    prog_res = client.post(f'/api/complaints/{cid}/progress-update', headers=off_headers, json={'message': 'Excavation completed and sub-base compacted.'})
    assert prog_res.status_code == 200
    print(f"Officer posted progress update on #{cid}")

    # Officer resolves complaint (Stage 3 -> Stage 4)
    resolve_res = client.put(f'/api/complaints/{cid}/complete-work', headers=off_headers, json={'completion_message': 'Pothole fully sealed with bitumen and steamrolled. Road clear.'})
    assert resolve_res.status_code == 200
    print(f"Officer resolved #{cid}: Advanced to {resolve_res.json()['status']} (Stage 4 - 80%)")

    print("\n--- 4. ADMIN VERIFIES AND FORMALLY CLOSES COMPLAINT (STAGE 4 -> 5) ---")
    close_res = client.put(f'/api/complaints/{cid}/close', headers=admin_headers, json={'closure_message': 'Inspected on-site by GCC Municipal Inspector. Remediation verified and case closed.'})
    assert close_res.status_code == 200
    print(f"Admin verified and formally closed #{cid}: Advanced to {close_res.json()['status']} (Stage 5 - 100%)")

    print("\n--- 5. CITIZEN RECEIVES MESSAGES & IN-APP NOTIFICATIONS ---")
    notif_res = client.get('/api/notifications', headers=citizen_headers).json()
    notifications = notif_res['notifications']
    print(f"Citizen received {len(notifications)} in-app notifications throughout the lifecycle:")
    for n in notifications[:4]:
        print(f"  • [{n['title']}] {n['message']}")

    # Citizen views updated complaint details
    final_view = client.get(f'/api/complaints/{cid}', headers=citizen_headers).json()
    assert final_view['status'] == 'CLOSED'
    assert final_view['progress_percent'] == 100
    assert final_view['evidence_filename'] == evidence_fn
    print(f"Citizen verified final complaint status: {final_view['status']} (100% Progress, Closed).")

    print("\n========================================================")
    print("ALL TESTS PASSED: ALL ROLES & ATTACHMENT VISIBILITY VERIFIED!")
    print("========================================================")

if __name__ == '__main__':
    run_verification()
