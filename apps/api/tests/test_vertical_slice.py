import io
import pytest
from fastapi.testclient import TestClient
from apps.api.app.main import app
from apps.api.app.core.database import SessionLocal
from apps.api.app.models.entities import Milestone, User
from apps.api.app.services.storage import storage_service

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["project"] == "GroundTruth"

def test_login_submitter_and_reviewer():
    # Test Submitter Login
    resp = client.post("/api/v1/auth/login", json={
        "email": "worker@groundtruth.local",
        "password": "password123"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "SUBMITTER"

    # Test Reviewer Login
    resp_rev = client.post("/api/v1/auth/login", json={
        "email": "reviewer@groundtruth.local",
        "password": "password123"
    })
    assert resp_rev.status_code == 200
    assert resp_rev.json()["role"] == "REVIEWER"

def test_evidence_submission_and_server_sha256_verification():
    # 1. Login as submitter
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "worker@groundtruth.local",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch seed milestone
    db = SessionLocal()
    milestone = db.query(Milestone).first()
    assert milestone is not None
    db.close()

    # 2. Upload dummy test image bytes
    test_image_bytes = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    # Actually create a valid JPEG byte sequence or PNG
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new("RGB", (640, 480), color="blue")
    img.save(buf, format="JPEG")
    real_jpeg_bytes = buf.getvalue()

    upload_data = {
        "milestone_id": milestone.id,
        "category": "REBAR_INSPECTION",
        "notes": "Foundation rebar grid verified before concrete pour",
        "capture_latitude": 28.6140,
        "capture_longitude": 77.2091,
        "client_capture_time": "2026-11-10T12:00:00Z"
    }

    files = {
        "file": ("rebar_grid.jpg", real_jpeg_bytes, "image/jpeg")
    }

    submit_resp = client.post(
        "/api/v1/evidence/submit",
        data=upload_data,
        files=files,
        headers=headers
    )
    assert submit_resp.status_code == 201
    evidence = submit_resp.json()
    evidence_id = evidence["id"]

    # Verify SHA-256 calculation on the server matches expected hash
    expected_hash = storage_service.compute_sha256(real_jpeg_bytes)
    assert evidence["sha256_hash"] == expected_hash

    # 3. Test Verification Endpoint (Server-Side Byte Recalculation)
    verify_resp = client.get(f"/api/v1/evidence/verify/{evidence_id}")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["is_valid"] is True
    assert verify_data["status"] == "INTEGRITY_VERIFIED"
    assert verify_data["computed_sha256"] == expected_hash

    # 4. Test RBAC: Submitter cannot approve evidence
    review_attempt = client.post(
        f"/api/v1/evidence/review/{evidence_id}",
        json={"decision": "APPROVED", "reason": "Self-approval"},
        headers=headers
    )
    assert review_attempt.status_code == 403

    # 5. Reviewer approves evidence
    rev_login = client.post("/api/v1/auth/login", json={
        "email": "reviewer@groundtruth.local",
        "password": "password123"
    })
    rev_token = rev_login.json()["access_token"]
    rev_headers = {"Authorization": f"Bearer {rev_token}"}

    review_success = client.post(
        f"/api/v1/evidence/review/{evidence_id}",
        json={"decision": "APPROVED", "reason": "Rebar spacing aligns with drawing rev-C"},
        headers=rev_headers
    )
    assert review_success.status_code == 200
    assert review_success.json()["decision"] == "APPROVED"

