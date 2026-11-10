import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from apps.api.app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="SUBMITTER")  # ADMIN, PROJECT_MANAGER, REVIEWER, SUBMITTER, AUDITOR
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    organization = relationship("Organization", back_populates="users")
    evidence_submissions = relationship("Evidence", back_populates="submitter")
    reviews = relationship("EvidenceReview", back_populates="reviewer")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    project_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    organization = relationship("Organization", back_populates="projects")
    sites = relationship("Site", back_populates="project")
    milestones = relationship("Milestone", back_populates="project")


class Site(Base):
    __tablename__ = "sites"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    geofence_radius_meters = Column(Float, default=100.0)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("Project", back_populates="sites")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sequence_number = Column(Integer, default=1)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    project = relationship("Project", back_populates="milestones")
    evidence_records = relationship("Evidence", back_populates="milestone")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    milestone_id = Column(String(36), ForeignKey("milestones.id"), nullable=False)
    submitted_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    category = Column(String(100), nullable=False)
    notes = Column(Text, nullable=True)

    # Cryptographic File Integrity & Storage (Server-Side)
    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(512), nullable=False, unique=True)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)

    # Perceptual Similarity Fingerprints (Milestone 3)
    phash = Column(String(64), nullable=True, index=True)
    dhash = Column(String(64), nullable=True, index=True)

    # Capture & Device Metadata (Distinguished from Server Receipt)
    client_capture_time = Column(DateTime, nullable=True)
    server_receipt_time = Column(DateTime, default=utc_now, nullable=False)
    capture_latitude = Column(Float, nullable=True)
    capture_longitude = Column(Float, nullable=True)
    gps_accuracy_meters = Column(Float, nullable=True)
    location_status = Column(String(50), default="UNVERIFIED")  # VERIFIED_IN_GEOFENCE, OUTSIDE_GEOFENCE, UNVERIFIED

    # Processing & Review State
    processing_status = Column(String(50), default="QUEUED")  # QUEUED, PROCESSING, COMPLETED, FAILED
    review_status = Column(String(50), default="PENDING_REVIEW")  # PENDING_REVIEW, APPROVED, REJECTED, CORRECTION_REQUESTED

    # Versioning & Corrective Action Lineage
    version_number = Column(Integer, default=1, nullable=False)
    superseded_evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=True)

    # Advisory AI summary (Separate from human decisions)
    ai_quality_score = Column(Float, nullable=True)
    ai_flags = Column(JSON, default=list)
    ai_recommendation = Column(String(50), nullable=True)  # ADVISORY: NORMAL_REVIEW, ATTENTION_REQUIRED, RECAPTURE_SUGGESTED

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    milestone = relationship("Milestone", back_populates="evidence_records")
    submitter = relationship("User", back_populates="evidence_submissions")
    reviews = relationship("EvidenceReview", back_populates="evidence")
    ai_findings = relationship("AIFinding", back_populates="evidence")
    prior_submission = relationship("Evidence", remote_side=[id], backref="resubmissions")


class ProjectSpecification(Base):
    __tablename__ = "project_specifications"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    document_code = Column(String(100), nullable=False)
    section_reference = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)  # REBAR, CONCRETE, DRAINAGE, SUBGRADE
    content = Column(Text, nullable=False)
    numeric_tolerance = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class EvidenceReview(Base):
    __tablename__ = "evidence_reviews"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # APPROVED, REJECTED, CORRECTION_REQUESTED
    reason = Column(Text, nullable=False)
    corrective_actions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    evidence = relationship("Evidence", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class AIFinding(Base):
    __tablename__ = "ai_findings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    evidence_id = Column(String(36), ForeignKey("evidence.id"), nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    finding_type = Column(String(100), nullable=False)  # QUALITY, DUPLICATE_CANDIDATE, DEFECT_SCREENING, OCR
    confidence = Column(Float, nullable=True)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    evidence = relationship("Evidence", back_populates="ai_findings")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    entity_type = Column(String(50), nullable=False)  # EVIDENCE, REVIEW, PROJECT, USER
    entity_id = Column(String(36), nullable=False)
    actor_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)  # EVIDENCE_SUBMITTED, REVIEW_DECIDED, INTEGRITY_VERIFIED, etc.
    changes = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=utc_now)

