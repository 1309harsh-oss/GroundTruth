from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

# API Envelope structures
class MetaEnvelope(BaseModel):
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ResponseEnvelope(BaseModel):
    data: Any
    meta: Optional[MetaEnvelope] = None

# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    display_name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SocialLoginRequest(BaseModel):
    provider: str  # google, facebook
    token: Optional[str] = None
    email: str
    display_name: str
    role: Optional[str] = "SUBMITTER"

class RegisterRequest(BaseModel):
    email: str
    display_name: str
    password: str
    role: Optional[str] = "SUBMITTER"

# User & Org Schemas
class UserCreate(BaseModel):
    organization_id: str
    email: str
    display_name: str
    password: str
    role: Optional[str] = "SUBMITTER"

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    organization_id: str
    status: str

    class Config:
        from_attributes = True

# Evidence Schemas
class EvidenceCreateMetadata(BaseModel):
    milestone_id: str
    category: str
    notes: Optional[str] = None
    client_capture_time: Optional[datetime] = None
    capture_latitude: Optional[float] = None
    capture_longitude: Optional[float] = None
    gps_accuracy_meters: Optional[float] = None
    superseded_evidence_id: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: str
    milestone_id: str
    submitted_by: str
    category: str
    notes: Optional[str]
    original_filename: str
    file_size_bytes: int
    mime_type: str
    sha256_hash: str
    client_capture_time: Optional[datetime]
    server_receipt_time: datetime
    capture_latitude: Optional[float]
    capture_longitude: Optional[float]
    location_status: str
    processing_status: str
    review_status: str
    version_number: int
    superseded_evidence_id: Optional[str] = None
    ai_quality_score: Optional[float]
    ai_recommendation: Optional[str]
    ai_flags: Optional[List[str]] = []
    created_at: datetime
    latest_review_reason: Optional[str] = None
    latest_review_corrective: Optional[str] = None

    class Config:
        from_attributes = True

# Verification Schemas
class EvidenceVerificationResponse(BaseModel):
    evidence_id: str
    status: str  # INTEGRITY_VERIFIED, INTEGRITY_COMPROMISED, NOT_FOUND
    is_valid: bool
    recorded_sha256: str
    computed_sha256: str
    original_filename: str
    file_size_bytes: int
    server_receipt_time: datetime
    review_status: str
    message: str

# Review Schemas
class ReviewDecisionCreate(BaseModel):
    decision: str  # APPROVED, REJECTED, CORRECTION_REQUESTED
    reason: str
    corrective_actions: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    evidence_id: str
    reviewer_id: str
    decision: str
    reason: str
    corrective_actions: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    actor_id: Optional[str]
    action: str
    changes: dict
    timestamp: datetime

    class Config:
        from_attributes = True

class EvidenceDetailResponse(BaseModel):
    evidence: EvidenceResponse
    reviews: List[ReviewResponse] = []
    audit_history: List[AuditLogResponse] = []
    lineage: List[EvidenceResponse] = []
