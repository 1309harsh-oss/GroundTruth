# Software Requirements Specification (SRS)

## 1. Purpose and scope

Specify the observable software behavior of GroundTruth's MVP and extension points.

## 2. External interfaces

- Web UI for all user roles.
- REST API `/api/v1`.
- Private object storage.
- PostgreSQL/PostGIS.
- Redis-backed background queue.
- OCR and vision model adapters.
- Optional notification and mapping providers.

## 3. Functional requirements

### Identity and access
- FR-001: The system shall authenticate users.
- FR-002: The system shall enforce role and project-scoped permissions server-side.
- FR-003: Administrators shall create, deactivate and assign users.
- FR-004: The system shall record security-relevant authentication and permission events.

### Projects and milestones
- FR-010: Authorized users shall create and update projects.
- FR-011: Projects shall contain sites/locations and milestones.
- FR-012: Milestones shall define required evidence categories and instructions.
- FR-013: Users shall see only projects they are authorized to access.

### Evidence submission
- FR-020: Authorized submitters shall upload supported image formats.
- FR-021: The system shall validate file size, MIME type, file signature and decodability.
- FR-022: The system shall preserve original file bytes.
- FR-023: The system shall compute SHA-256 server-side.
- FR-024: The system shall record uploader, project, milestone, server receipt time and available capture metadata.
- FR-025: The system shall record metadata source and uncertainty.
- FR-026: The system shall assign a unique evidence ID.
- FR-027: The system shall queue asynchronous analysis.

### AI screening
- FR-030: The system shall assess configured image quality indicators.
- FR-031: The system shall run OCR when enabled.
- FR-032: The system shall check exact and perceptual similarity against permitted prior evidence.
- FR-033: The system shall run only defect classes supported by the active model.
- FR-034: Findings shall include model name/version, timestamp, class, confidence and optional region coordinates.
- FR-035: The system shall label AI results as preliminary.
- FR-036: Failed analysis shall be visible and retryable by authorized operations users.

### Review and correction
- FR-040: Reviewers shall access an assigned evidence queue.
- FR-041: Reviewers shall see original evidence, metadata, AI findings and relevant milestone requirements.
- FR-042: Reviewers shall approve, reject or request correction.
- FR-043: Reviewer decisions shall record reviewer, timestamp, reason and notes.
- FR-044: A correction request shall create a resubmission path.
- FR-045: The system shall retain links to previous submissions.
- FR-046: AI shall not perform final approval or rejection.

### Verification and reporting
- FR-050: Authorized users shall verify an evidence record's stored hash.
- FR-051: The system shall show hash match or mismatch without implying capture authenticity.
- FR-052: Authorized users shall search/filter evidence by project, milestone, status, date and submitter.
- FR-053: The system shall provide project and milestone dashboards.
- FR-054: The system may generate a QR code containing an opaque verification URL/ID.
- FR-055: Public verification shall expose only explicitly approved fields.

### Audit
- FR-060: The system shall append an audit event for important record and permission changes.
- FR-061: Audit events shall identify actor, action, target, timestamp and correlation ID.
- FR-062: Normal application users shall not edit or delete audit events.
- FR-063: Administrative corrections shall themselves be audited.

## 4. Data requirements

Core entities: Organization, User, Role, Project, Site, Milestone, EvidenceRequirement, Evidence, EvidenceFile, EvidenceMetadata, AIAnalysisRun, AIFinding, Review, CorrectiveAction, AuditEvent, KnowledgeDocument, DocumentChunk, Notification.

## 5. State and business rules

- Evidence must be associated with a project and milestone.
- The server-generated SHA-256 is authoritative for stored file bytes.
- Capture metadata is untrusted input until corroborated.
- No AI result can transition evidence directly to APPROVED.
- Rejected records remain available according to retention policy.
- A resubmission references the prior evidence record.

## 6. Error handling

Return stable error codes and safe messages. Never expose stack traces, storage credentials, signed URLs or internal paths. Use standard HTTP status codes and a consistent JSON error envelope.

## 7. Non-functional requirements

See `GRD.md` and `TRD.md`. All requirements must be validated through the test plan.
