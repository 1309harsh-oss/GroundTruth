# Open Questions — Product & Engineering Baseline

This document tracks unresolved product decisions, required domain expert inputs, and assumptions made for local/MVP development according to `ANTIGRAVITY.md` and `OPEN_QUESTIONS.md`.

## Open Questions & Current MVP Assumptions

### 1. Pilot Infrastructure Asset Category & Supported Defect Classes
- **Question:** Which initial pilot category (e.g. roads, drainage, public buildings) and specific defect classes are in scope?
- **MVP Assumption:** Initial focus is on general civil construction & road works (e.g. surface cracks, uncompacted subgrade, rebar exposure, waterlogging). The model inference is decoupled via an advisory AI provider adapter interface.

### 2. Mandatory vs. Optional GPS & Geofencing Policy
- **Question:** Is GPS location mandatory per milestone, and what is the standard geofence tolerance?
- **MVP Assumption:** GPS coordinates are treated as untrusted metadata provided by the client device. If GPS is absent, the upload is accepted but flagged with `location_status: "UNVERIFIED_OR_MISSING"` for human reviewer scrutiny. Geofencing flags coordinates outside 100m of the site centroid as warning alerts.

### 3. Public Verification Exposure Scope
- **Question:** Which evidence fields may be publicly verified without authentication?
- **MVP Assumption:** Only non-sensitive verification metadata is exposed publicly (Evidence UUID, verification timestamp, SHA-256 hash match status, milestone title, review status, and capture timestamp). Sensitive reviewer comments, internal audit events, and contractor details remain restricted to authenticated users.

### 4. Background Job & Storage Infrastructure in Local vs Production
- **Question:** In environments without Docker/Redis/PostGIS running locally, how should jobs and files be persisted?
- **MVP Assumption:** Storage is abstracted behind a clean storage adapter (local filesystem / S3-compatible). Database uses SQLAlchemy ORM configured to work seamlessly on SQLite for local zero-dependency testing and PostgreSQL/PostGIS for containerized/cloud deployment. Background worker runs asynchronously via FastAPI background tasks or dedicated worker process.

### 5. Multi-Reviewer Escalation & Dual Approval
- **Question:** Does critical milestone evidence require multi-party sign-off (two-person rule)?
- **MVP Assumption:** The data model supports `evidence_reviews` as a 1-to-many relationship, allowing multiple review records. For the first vertical slice, a single authorized reviewer decision determines milestone progression.

