# Product Requirements Document (PRD)

## 1. Executive summary

GroundTruth converts infrastructure photographs and related project information into structured, traceable evidence records. It helps project owners, field inspectors, engineers, contractors and auditors assess whether evidence is authentic at the file-integrity level, relevant to a project milestone, visually adequate and properly reviewed.

## 2. Problem statement

Infrastructure progress may be reported using photographs whose provenance, location, timestamp, relevance, completeness or integrity is difficult to establish consistently. Manual review alone can miss duplicate submissions, image-quality problems, visible anomalies and gaps in milestone evidence. Decisions and corrective actions may also be scattered across systems.

GroundTruth provides a controlled workflow for evidence capture, automated screening, human review, corrective action and traceable verification.

## 3. Product goals

1. Associate every submission with a project, milestone, submitter and evidence record.
2. Preserve original submitted files and verify their byte-level integrity.
3. Collect capture metadata and clearly distinguish device-provided data from independently verified data.
4. Assess image quality and extract visible text where useful.
5. Screen for selected visible construction anomalies using computer vision.
6. Identify exact and visually similar submissions for reviewer attention.
7. Compare evidence with milestone requirements and prior submissions.
8. Route AI findings to authorized human reviewers.
9. Record decisions, reasons, revisions and audit events.
10. Provide controlled verification through an evidence ID or QR code.

## 4. Non-goals

- Replacing civil engineers, site inspectors or statutory authorities.
- Certifying structural safety from photographs alone.
- Automatically approving payments or contractual completion.
- Guaranteeing GPS authenticity from device metadata.
- Proving that a scene is genuine solely through SHA-256.
- Building blockchain, smart contracts, wallets, NFTs or token systems.
- Supporting every infrastructure category with high accuracy in the first release.

## 5. Users and roles

| Role | Primary capabilities |
|---|---|
| Platform administrator | Tenant setup, user/role administration, global configuration |
| Project owner / department | Create projects, milestones, requirements and reviewer assignments |
| Project manager | Monitor progress, evidence status and corrective actions |
| Contractor / worker | Submit evidence for assigned projects and milestones |
| Field inspector | Capture evidence, add observations and review assigned sites |
| Technical reviewer / engineer | Inspect evidence, AI findings and milestone requirements; decide |
| Auditor | Read permitted records, decisions and audit history |
| Public verifier | Verify a public verification ID/QR result where explicitly enabled |

Use least-privilege access. A person may have multiple roles, scoped by organization, project and assignment.

## 6. Core user journeys

### Submit evidence
1. User signs in.
2. Selects assigned project and milestone.
3. Captures a new photograph in the application or uploads an allowed file.
4. Application records available device location, capture time and capture method.
5. User enters optional notes and required evidence category.
6. Server validates file type/size, stores the original, computes SHA-256 and creates the evidence record.
7. Processing jobs are queued.

### Automated screening
1. Validate file and metadata.
2. Assess blur, exposure, resolution and obstruction.
3. Extract OCR text if applicable.
4. Run exact and perceptual duplicate checks.
5. Run the enabled vision model for the milestone's supported defect classes.
6. Retrieve relevant project specifications and milestone requirements.
7. Create findings with model/version, confidence, evidence region and explanation.
8. Set a routing recommendation: recapture, reviewer attention or normal review.
9. Never treat the recommendation as final approval.

### Human review
1. Reviewer opens assigned queue.
2. Reviews original image, metadata, AI annotations, prior evidence and requirements.
3. Chooses approve, reject or request correction.
4. Enters a reason and, where needed, corrective instructions.
5. System records reviewer identity, time, decision and audit event.
6. Submitter receives status and next action.
7. Corrected submissions are linked to prior submissions; prior evidence is retained.

### Verification
1. Authorized user or public verifier enters evidence ID or scans QR.
2. System checks access policy and record status.
3. System recomputes SHA-256 against the stored original when file access is authorized.
4. Shows integrity match/mismatch, review status and permitted metadata.
5. Clearly distinguishes file integrity from construction quality or capture authenticity.

## 7. Functional modules

- Authentication and authorization.
- Organization and project management.
- Milestone and evidence requirement management.
- Evidence capture/upload.
- Metadata and geospatial validation.
- Original file storage and integrity service.
- AI processing orchestration.
- OCR and computer vision.
- Duplicate/similarity detection.
- Specification knowledge base and RAG retrieval.
- Reviewer queue and decision management.
- Corrective action and resubmission.
- GIS map and project dashboard.
- QR/public verification.
- Audit log and reporting.
- Notifications.

## 8. MVP scope

Must-have:
- Login and role-based authorization.
- Project and milestone CRUD.
- Evidence upload with original-file preservation.
- SHA-256 fingerprint.
- GPS metadata capture when permission is granted.
- Basic image quality checks.
- OCR extraction.
- Basic duplicate detection.
- One narrowly defined infrastructure category and a small, explicit defect taxonomy.
- Human review queue and approve/reject/request-correction actions.
- Evidence history and audit trail.
- Reviewer dashboard and evidence detail page.

Should-have:
- Map view with project geofence.
- Milestone-specific required photo checklist.
- QR verification for selected records.
- RAG retrieval over project specifications.
- Before/after comparison.

Out of scope for first MVP:
- Universal road/building defect intelligence.
- Automated engineering certification.
- Predictive maintenance.
- Government system integrations without approved interfaces.
- Fully offline synchronization unless the team explicitly prioritizes it.

## 9. Product states

Evidence lifecycle:
`DRAFT → UPLOADED → PROCESSING → AI_SCREENED → PENDING_REVIEW → APPROVED | REJECTED | CORRECTION_REQUESTED`

Additional states:
- `PROCESSING_FAILED`
- `WITHDRAWN` (only where policy permits, with audit record)
- `SUPERSEDED` (for a later submission linked to an earlier version)

Do not delete rejected or superseded evidence as part of normal workflow.

## 10. Success metrics

- Percentage of submissions with complete required metadata.
- Median upload-to-AI-screening time.
- Median reviewer turnaround time.
- Percentage of submissions returned for recapture.
- Duplicate-image alert precision and reviewer-confirmed rate.
- Defect model precision/recall by class and site conditions.
- Reviewer override rate for AI recommendations.
- Percentage of decisions with reason codes and notes.
- Evidence integrity verification success rate.
- System availability and processing failure rate.

Do not optimize for a high AI approval rate. Optimize for useful screening, low false confidence and better review efficiency.

## 11. Acceptance criteria

- Every accepted upload has a unique evidence ID and stored original.
- SHA-256 is computed server-side from the exact stored original bytes.
- Re-downloaded original bytes produce the same SHA-256.
- Metadata fields retain source and confidence/provenance.
- AI findings include model version and processing timestamp.
- Reviewer decisions require an authorized role and a reason where configured.
- All status changes create audit events.
- A corrected submission links to the earlier evidence record.
- Unauthorized users cannot access original evidence.
- AI output is clearly labelled as preliminary.
