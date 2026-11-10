# Database Design and Data Dictionary

## 1. Database choice

PostgreSQL with PostGIS. Use object storage for binary images and documents. Use `pgvector` optionally for embeddings if it fits the operational requirements.

## 2. Core entities

### organizations
- `id UUID PK`
- `name`
- `slug`
- `status`
- `created_at`, `updated_at`

### users
- `id UUID PK`
- `organization_id UUID FK`
- `email` (unique within policy scope)
- `display_name`
- `password_hash` or external identity subject
- `status`
- `created_at`, `updated_at`

### roles / user_roles
- Role definitions and user assignments.
- Include scope type and scope ID where project-level roles are needed.

### projects
- `id UUID PK`
- `organization_id UUID FK`
- `project_code`
- `name`, `description`
- `status`
- `start_date`, `target_end_date`
- `created_at`, `updated_at`

### sites
- `id UUID PK`
- `project_id UUID FK`
- `name`
- `location GEOGRAPHY(Point,4326)` nullable
- `geofence GEOMETRY(Polygon,4326)` nullable
- `address`
- `created_at`, `updated_at`

### milestones
- `id UUID PK`
- `project_id UUID FK`
- `name`, `description`
- `sequence_number`
- `status`
- `due_date`
- `created_at`, `updated_at`

### evidence_requirements
- `id UUID PK`
- `milestone_id UUID FK`
- `category`
- `description`
- `required_count`
- `required_view_guidance`
- `validation_rules JSONB`
- `is_mandatory`

### evidence
- `id UUID PK`
- `organization_id UUID FK`
- `project_id UUID FK`
- `milestone_id UUID FK`
- `site_id UUID FK nullable`
- `submitted_by UUID FK`
- `parent_evidence_id UUID FK nullable`
- `status`
- `capture_method` (`in_app`, `gallery_upload`, `other`)
- `captured_at_device` nullable
- `received_at_server`
- `latitude`, `longitude`, `gps_accuracy_m` nullable
- `location_source`
- `notes`
- `created_at`, `updated_at`

### evidence_files
- `id UUID PK`
- `evidence_id UUID FK`
- `object_key`
- `file_role` (`original`, `thumbnail`, `annotated`, `derivative`)
- `original_filename` (restricted access)
- `mime_type`
- `size_bytes`
- `width`, `height`
- `sha256`
- `created_at`

### evidence_metadata
- `id UUID PK`
- `evidence_id UUID FK`
- `metadata_key`
- `metadata_value JSONB`
- `source`
- `confidence_or_accuracy` nullable
- `created_at`

### ai_analysis_runs
- `id UUID PK`
- `evidence_id UUID FK`
- `pipeline_version`
- `status`
- `model_manifest JSONB`
- `started_at`, `completed_at`
- `error_code`, `error_message_safe`

### ai_findings
- `id UUID PK`
- `analysis_run_id UUID FK`
- `finding_type`
- `class_label`
- `confidence`
- `severity` nullable
- `region_json` nullable
- `description`
- `source_reference` nullable
- `created_at`

### reviews
- `id UUID PK`
- `evidence_id UUID FK`
- `reviewer_id UUID FK`
- `decision` (`approved`, `rejected`, `correction_requested`)
- `reason_code`
- `comments`
- `reviewed_at`

### corrective_actions
- `id UUID PK`
- `evidence_id UUID FK`
- `assigned_to UUID FK nullable`
- `description`
- `status`
- `due_at`
- `closed_at`

### audit_events
- `id UUID PK`
- `organization_id UUID FK`
- `actor_id UUID FK nullable`
- `action`
- `entity_type`, `entity_id`
- `before_state JSONB` (redacted)
- `after_state JSONB` (redacted)
- `correlation_id`
- `ip_hash_or_security_context` where policy permits
- `created_at`

### knowledge_documents / document_chunks
Store approved project specifications, source version, access scope, text chunks, page/section citations and optional vector embeddings.

## 3. Relationships

- Organization 1—many Projects and Users.
- Project 1—many Sites and Milestones.
- Milestone 1—many EvidenceRequirements and Evidence.
- Evidence 1—many Files, Metadata records, AnalysisRuns, Reviews and CorrectiveActions.
- Evidence may reference a prior Evidence record through `parent_evidence_id`.
- AnalysisRun 1—many AIFindings.
- User 1—many submissions and reviews.
- Every important mutation creates an AuditEvent.

## 4. Indexes

- Foreign-key indexes.
- `evidence(project_id, milestone_id, status, received_at_server)`.
- `evidence(submitted_by, received_at_server)`.
- `evidence_files(sha256)` for exact duplicate lookup, scoped by access policy.
- GiST index on site and evidence geographic points.
- `ai_findings(analysis_run_id, finding_type)`.
- `audit_events(entity_type, entity_id, created_at)`.
- Full-text/vector indexes for knowledge retrieval as appropriate.

## 5. Data integrity rules

- SHA-256 stored as 64-character lowercase hexadecimal or binary representation.
- Hash must be computed server-side from original bytes.
- Do not update original file hash after upload; a new file creates a new file/evidence version.
- Use database transactions for evidence state transitions and review decisions.
- Audit events are append-only at the application permission level.
- Enforce organization/project scope in queries, not only UI filters.
- Define retention, legal hold and deletion behavior before production.

## 6. Migration guidance

Use Alembic. Migrations must be committed, tested on a clean database and include indexes/constraints. Seed only non-production demo data.
