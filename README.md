# GroundTruth — Intelligent Infrastructure Evidence Verification

**Project:** GroundTruth  
**Team:** Code Sprinters  
**Purpose:** Verify the authenticity, relevance, technical sufficiency and review status of infrastructure evidence submitted against project milestones.

## Product boundary

GroundTruth is a conventional web-based software platform. It is **not a blockchain project**. It does not use blockchain, smart contracts, wallets, tokens, NFTs or on-chain storage.

Evidence integrity is provided through:
- SHA-256 hashes of original file bytes.
- Secure object storage with versioning and access controls.
- Perceptual similarity checks for potential duplicate/reused images.
- Metadata and location consistency checks.
- Append-only application audit events and reviewer history.

A SHA-256 hash proves that a file matches a previously recorded byte sequence. It does not, by itself, prove when, where or how a photograph was captured, nor that the depicted work is genuine.

## Documentation map

- `PRD.md` — product vision, users, scope and acceptance criteria.
- `TRD.md` — technical requirements and implementation constraints.
- `BRD.md` — business objectives, stakeholders and operational value.
- `GRD.md` — general, non-functional and platform requirements.
- `SRS.md` — functional and non-functional software requirements.
- `CS.md` — coding standards and repository conventions.
- `ARCHITECTURE.md` — system components, boundaries and architecture decisions.
- `WORKFLOWS.md` — end-to-end business and system workflows.
- `DATABASE.md` — relational data model and migration guidance.
- `API_SPEC.md` — REST API contract baseline.
- `AI_SPEC.md` — computer vision, OCR, similarity and RAG design.
- `SECURITY.md` — security, privacy, evidence integrity and audit requirements.
- `TEST_PLAN.md` — test strategy and acceptance scenarios.
- `DEPLOYMENT.md` — environments, CI/CD, operations and deployment.
- `ROADMAP.md` — phased implementation plan.
- `ANTIGRAVITY.md` — instructions for the AI coding agent.

## Suggested initial stack

- Frontend: Next.js + TypeScript + Tailwind CSS.
- Backend: Python + FastAPI.
- Database: PostgreSQL + PostGIS.
- Object storage: S3-compatible storage.
- Image processing: OpenCV.
- OCR: PaddleOCR.
- Vision: a task-appropriate object detection / segmentation model, selected after dataset evaluation.
- Similarity: perceptual hashes plus optional visual embeddings.
- RAG: PostgreSQL with pgvector or a separately operated vector store.
- Background jobs: Redis + Celery or an equivalent queue.
- Maps: Leaflet.
- Deployment: Docker; deploy frontend, API, worker and database as separately managed services.

Treat this as the recommended baseline, not a claim that every integration has already been configured.

## First-run principle

Build a working vertical slice before adding advanced AI:
1. Authenticate a user.
2. Create a project and milestone.
3. Capture/upload evidence.
4. Preserve original bytes and calculate SHA-256.
5. Save metadata and processing status.
6. Run quality checks.
7. Put evidence into a reviewer queue.
8. Record approve / reject / request-correction decisions.
9. Verify the stored file against its recorded hash.

## Critical product rule

AI findings are decision support. AI must not independently issue final construction acceptance, certify structural safety, release payments or override an authorized human reviewer.
