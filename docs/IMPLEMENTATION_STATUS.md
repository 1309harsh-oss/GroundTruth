# GroundTruth — Implementation Status

Last updated: Initial Milestone - Architecture & First Vertical Slice

## Milestone Progress Summary

| Phase / Milestone | Status | Details |
|---|---|---|
| **0. Architecture & Foundations** | **COMPLETED** | System specifications reviewed, discrepancies identified, folder structure established, dependencies confirmed. |
| **1. Core Domain & Auth (RBAC)** | **COMPLETED** | Organization, User, Roles, Projects, Sites, Milestones data model, JWT authentication, RBAC middleware. |
| **2. Human Review & Correction Lineage** | **COMPLETED** | Reviewer queues, approve/reject/correction workflow, corrective action requirements, versioned resubmissions linked to prior evidence, full audit event tracking. |
| **3. Evidence Ingestion & SHA-256 Verification** | **COMPLETED** | Server-side cryptographic SHA-256 calculation, immutable storage, metadata extraction, tampering detection. |
| **4. Asynchronous Quality & Perceptual Duplicate Screening** | **COMPLETED** | Image quality assessment (resolution, exposure, contrast metrics), perceptual hashing (`imagehash` dHash/pHash), near-duplicate candidate detection with Hamming distance calculation, advisory screening separated from human approval. |
| **5. Dynamic UI & Live Backend Engine** | **COMPLETED** | Dynamic responsive single-page portal (`apps/web/index.html`) connecting live to FastAPI engine on `http://localhost:8000`. Full support for evidence submission, live queue review, public verification, and audit trail ledger. |

---

## Detailed Component Status

### Backend (`apps/api`)
- [x] Application scaffold & config (`FastAPI`, `Pydantic v2`, `SQLAlchemy`)
- [x] SQLite / PostgreSQL compatible schema for local development & production PostGIS
- [x] Authentication & RBAC (Bearer JWT, password hashing)
- [x] Core models: Organization, User, Role, Project, Site, Milestone, Evidence, AuditLog
- [x] Evidence ingestion endpoint with server-side SHA-256 hash generation
- [x] Evidence verification endpoint (re-hashes raw bytes and compares against immutable digest)
- [x] Review decision endpoints with audit trail
- [x] Unit & integration tests for hashing, auth, upload validation

### Background Worker (`apps/worker` / `apps/api/app/workers`)
- [x] Job queue abstraction (async worker pipeline)
- [x] Server-side image validation (magic bytes, dimensions, format verification)
- [x] Quality assessment (blur, resolution, exposure checks)
- [x] Advisory AI screening placeholder decoupled from human approval

### Frontend (`apps/web`)
- [x] Submitter interface (evidence upload, metadata input)
- [x] Reviewer queue (inspect findings, approve/reject/request correction)
- [x] Public verification interface (SHA-256 verification, status inspection)

---

## Technical Constraints Respected
- **Strictly No Blockchain**: Implemented using conventional SHA-256 hashing, PostgreSQL/SQLite, object storage, and append-only audit tables.
- **AI Advisory Only**: AI cannot approve or reject evidence; decisions are recorded strictly under authenticated human reviewer IDs.
- **Server-Side Integrity**: Hashes are computed from server-received bytes before storage, preserving raw originals immutably.

