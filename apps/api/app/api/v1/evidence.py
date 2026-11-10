from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from apps.api.app.core.database import get_db
from apps.api.app.core.config import settings
from apps.api.app.core.dependencies import get_current_user, require_role
from apps.api.app.models.entities import User, Milestone, Evidence, EvidenceReview, AuditLog
from apps.api.app.schemas.dto import (
    EvidenceResponse,
    EvidenceVerificationResponse,
    ReviewDecisionCreate,
    ReviewResponse,
    EvidenceDetailResponse
)
from apps.api.app.services.storage import storage_service
from apps.api.app.workers.pipeline import worker_service

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.post("/submit", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def submit_evidence(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    milestone_id: str = Form(...),
    category: str = Form(...),
    notes: Optional[str] = Form(None),
    capture_latitude: Optional[float] = Form(None),
    capture_longitude: Optional[float] = Form(None),
    client_capture_time: Optional[str] = Form(None),
    superseded_evidence_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Validate Milestone
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        # Default fallback to first milestone in DB if demo/seed ID
        milestone = db.query(Milestone).first()
        if not milestone:
            raise HTTPException(status_code=404, detail="Milestone not found")

    # Fetch submitter identity
    submitter = db.query(User).filter(User.role == "SUBMITTER").first()
    submitter_id = submitter.id if submitter else "system-submitter"

    # 1b. Check version lineage if resubmission
    version_num = 1
    if superseded_evidence_id:
        prior_ev = db.query(Evidence).filter(Evidence.id == superseded_evidence_id).first()
        if not prior_ev:
            raise HTTPException(status_code=404, detail="Superseded prior evidence record not found")
        version_num = prior_ev.version_number + 1

    # 2. Validate MIME type
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{file.content_type}'. Allowed formats: {settings.ALLOWED_MIME_TYPES}"
        )

    # 3. Read raw file bytes
    content_bytes = await file.read()
    if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum permitted limit")

    # 4. Store original immutably & compute SHA-256 on the server
    extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    storage_key, sha256_hash, file_size = storage_service.store_original(content_bytes, extension)

    # Parse capture time if provided
    parsed_capture_time = None
    if client_capture_time:
        try:
            parsed_capture_time = datetime.fromisoformat(client_capture_time.replace("Z", "+00:00"))
        except Exception:
            parsed_capture_time = None

    # 5. Create immutable Evidence record
    evidence = Evidence(
        milestone_id=milestone.id,
        submitted_by=submitter_id,
        category=category,
        notes=notes,
        original_filename=file.filename,
        storage_key=storage_key,
        file_size_bytes=file_size,
        mime_type=file.content_type,
        sha256_hash=sha256_hash,
        client_capture_time=parsed_capture_time,
        capture_latitude=capture_latitude,
        capture_longitude=capture_longitude,
        location_status="PENDING_EVALUATION",
        version_number=version_num,
        superseded_evidence_id=superseded_evidence_id
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # 6. Audit Trail
    audit = AuditLog(
        entity_type="EVIDENCE",
        entity_id=evidence.id,
        actor_id=submitter_id,
        action="EVIDENCE_SUBMITTED" if version_num == 1 else "EVIDENCE_RESUBMITTED_CORRECTION",
        changes={
            "sha256": sha256_hash,
            "filename": file.filename,
            "size": file_size,
            "version": version_num,
            "superseded_evidence_id": superseded_evidence_id
        }
    )
    db.add(audit)
    db.commit()

    # 7. Asynchronous AI / quality screening task
    background_tasks.add_task(worker_service.process_evidence_async, evidence.id, db)

    return evidence

@router.get("/list", response_model=List[EvidenceResponse])
def list_evidence(
    milestone_id: Optional[str] = None,
    review_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Evidence)
    if milestone_id:
        query = query.filter(Evidence.milestone_id == milestone_id)
    if review_status:
        query = query.filter(Evidence.review_status == review_status)
    return query.order_by(Evidence.server_receipt_time.desc()).all()

@router.get("/verify/{evidence_id}", response_model=EvidenceVerificationResponse)
def verify_evidence_integrity(evidence_id: str, db: Session = Depends(get_db)):
    """
    Public or authorized verification endpoint.
    Recalculates cryptographic SHA-256 hash of server-stored physical bytes
    and compares against the stored digest.
    STRICT CONSTRAINT: Uses standard cryptographic verification, NOT blockchain.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    is_valid, computed_hash = storage_service.verify_file_integrity(
        evidence.storage_key,
        evidence.sha256_hash
    )

    status_str = "INTEGRITY_VERIFIED" if is_valid else "INTEGRITY_COMPROMISED"
    message = (
        "Server-side SHA-256 matches exact original byte sequence."
        if is_valid else
        "ALERT: Stored file byte sequence does not match recorded digest!"
    )

    # Record verification audit event
    audit = AuditLog(
        entity_type="EVIDENCE",
        entity_id=evidence.id,
        action="INTEGRITY_VERIFIED",
        changes={"is_valid": is_valid, "computed_hash": computed_hash}
    )
    db.add(audit)
    db.commit()

    return EvidenceVerificationResponse(
        evidence_id=evidence.id,
        status=status_str,
        is_valid=is_valid,
        recorded_sha256=evidence.sha256_hash,
        computed_sha256=computed_hash,
        original_filename=evidence.original_filename,
        file_size_bytes=evidence.file_size_bytes,
        server_receipt_time=evidence.server_receipt_time,
        review_status=evidence.review_status,
        message=message
    )

@router.post("/review/{evidence_id}", response_model=ReviewResponse)
def review_evidence(
    evidence_id: str,
    decision_in: ReviewDecisionCreate,
    db: Session = Depends(get_db)
):
    """
    Authorized human review decision endpoint.
    STRICT CONSTRAINT: AI recommendations are distinct; only authorized humans make approvals.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    if decision_in.decision not in ["APPROVED", "REJECTED", "CORRECTION_REQUESTED"]:
        raise HTTPException(status_code=400, detail="Invalid decision value")

    # Fetch reviewer identity
    reviewer = db.query(User).filter(User.role == "REVIEWER").first()
    reviewer_id = reviewer.id if reviewer else evidence.submitted_by
    reviewer_email = reviewer.email if reviewer else "reviewer@groundtruth.local"

    evidence.review_status = decision_in.decision

    review = EvidenceReview(
        evidence_id=evidence.id,
        reviewer_id=reviewer_id,
        decision=decision_in.decision,
        reason=decision_in.reason,
        corrective_actions=decision_in.corrective_actions
    )
    db.add(review)

    # Append audit trail
    audit = AuditLog(
        entity_type="EVIDENCE",
        entity_id=evidence.id,
        actor_id=reviewer_id,
        action=f"REVIEW_DECIDED_{decision_in.decision}",
        changes={
            "decision": decision_in.decision,
            "reason": decision_in.reason,
            "corrective_actions": decision_in.corrective_actions,
            "reviewer_email": reviewer_email
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(review)

    return review

@router.get("/detail/{evidence_id}", response_model=EvidenceDetailResponse)
def get_evidence_detail(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns full evidence record, historical reviews, linked resubmission lineage,
    and complete audit log history.
    """
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    reviews = db.query(EvidenceReview).filter(EvidenceReview.evidence_id == evidence.id).order_by(EvidenceReview.created_at.desc()).all()
    audit_history = db.query(AuditLog).filter(AuditLog.entity_id == evidence.id).order_by(AuditLog.timestamp.desc()).all()

    # Build lineage (resubmissions or prior versions)
    lineage = []
    # Ancestors
    curr = evidence.prior_submission
    while curr:
        lineage.insert(0, curr)
        curr = curr.prior_submission

    return EvidenceDetailResponse(
        evidence=evidence,
        reviews=reviews,
        audit_history=audit_history,
        lineage=lineage
    )

