# Technical Requirements Document (TRD)

## 1. Architecture baseline

Use a modular monolith initially, with independently deployable background workers. Avoid premature microservices. Keep clear domain boundaries so high-load modules can be extracted later.

### Applications
- `apps/web`: Next.js user interface.
- `apps/api`: FastAPI REST API.
- `apps/worker`: asynchronous AI and file-processing jobs.
- `packages/shared`: shared API schemas/types where practical.
- `infra`: Docker, migrations, deployment and observability configuration.
- `docs`: project documentation.

## 2. Runtime components

1. Browser/mobile-responsive web client.
2. API gateway/reverse proxy.
3. FastAPI application.
4. PostgreSQL with PostGIS.
5. S3-compatible object storage.
6. Redis queue/cache.
7. Celery worker(s) for image/OCR/vision tasks.
8. AI model runtime (local or managed; isolate behind adapters).
9. RAG retrieval service and document ingestion jobs.
10. Notification provider adapter.
11. Monitoring/logging/metrics stack.

## 3. Technical requirements

- All API traffic over HTTPS.
- JSON REST APIs under `/api/v1`.
- UUID identifiers for externally exposed resources.
- UTC timestamps in storage; render local time in UI.
- Database migrations must be versioned and reversible where feasible.
- Original uploaded files are immutable after acceptance.
- File storage keys must not expose user-supplied filenames or personal information.
- Large file processing must be asynchronous.
- API requests must be idempotent where retries can create duplicate records.
- AI processing jobs must be retryable and deduplicated by evidence/version and pipeline version.
- Enforce tenant, organization, project and role scope in backend authorization.
- Use signed, short-lived object URLs for permitted file access.
- Keep secrets in environment/secret management, never source control.
- Define rate limits and upload limits.
- Record model version, configuration and processing result.

## 4. File pipeline

1. Receive upload to a quarantine/staging area.
2. Validate extension, MIME type, magic bytes, file size and decodability.
3. Malware scan where infrastructure supports it.
4. Compute SHA-256 on server-side bytes.
5. Store immutable original in private object storage.
6. Persist metadata and file record.
7. Queue processing job.
8. Generate derivatives (thumbnail, normalized preview, annotated image) in separate object keys.
9. Never overwrite original bytes.
10. Recompute hash during integrity verification or scheduled integrity audit.

## 5. Geospatial requirements

- Use PostGIS `geography(Point, 4326)` or geometry with explicit SRID.
- Store latitude and longitude as numeric coordinates and spatial point.
- Record source: device GPS, EXIF, manually entered, server-observed or external.
- Store reported accuracy radius when available.
- Project geofence checks must consider GPS accuracy and configured tolerance.
- A geofence result is a signal, not proof of physical presence.
- Do not silently replace missing GPS with IP-derived location.

## 6. AI execution requirements

- Run CPU/GPU-heavy tasks in workers, not request threads.
- Each task has status, attempt count, start/end time, error category and pipeline version.
- Store structured outputs using versioned schemas.
- Store confidence values as model outputs, not guaranteed probabilities unless calibrated.
- Thresholds must be configurable per model/class and validated on held-out data.
- Keep human override and feedback data separate from model labels until quality review.
- Model deployment requires evaluation, rollback and version pinning.

## 7. RAG requirements

- Ingest approved project specifications, BOQs, drawings converted to accessible text where licensed, inspection checklists and relevant manuals.
- Store document provenance, version, owner, upload date and access scope.
- Chunk documents with page/section references.
- Retrieve only documents the current user is authorized to access.
- Return citations to source document and page/section.
- RAG may explain applicable requirements; it must not invent a requirement when retrieval is empty.
- Use deterministic rule checks for numeric requirements where possible; do not rely on free-form LLM interpretation alone.

## 8. Performance targets (initial engineering targets)

These are targets to validate, not guaranteed current performance:
- Standard API read/write p95 under 500 ms excluding uploads and AI processing.
- Upload acknowledgement under 2 seconds after safe staging for typical files.
- AI screening asynchronous; target p95 under 90 seconds for the initial pipeline on selected hardware.
- Dashboard initial render under 3 seconds on a reasonable broadband connection.
- Support resumable or multipart upload if large files become common.
- Design for horizontal scaling of stateless API and worker processes.

## 9. Reliability

- Database backups and restore drills.
- Object storage versioning/retention policy.
- Queue retry with exponential backoff and dead-letter handling.
- Idempotent worker processing.
- Health/readiness endpoints.
- Graceful degradation if AI provider is unavailable: retain evidence and mark AI processing pending/failed; do not block human workflow indefinitely.

## 10. Architecture decision records

Maintain ADRs for:
- Modular monolith versus services.
- Object storage provider.
- AI model selection and hosting.
- RAG/vector storage.
- Tenant isolation strategy.
- Evidence retention and deletion policy.
- Public verification data exposure.
