# REST API Specification (Baseline)

Base path: `/api/v1`  
Format: JSON unless an endpoint explicitly handles binary upload.  
Authentication: secure session or bearer access token according to selected identity design.

## 1. Conventions

Success envelope:
```json
{
  "data": {},
  "meta": {
    "request_id": "uuid"
  }
}
```

Error envelope:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The uploaded file is not supported.",
    "details": []
  },
  "meta": {
    "request_id": "uuid"
  }
}
```

Use cursor or page-based pagination consistently. Never expose private object keys.

## 2. Authentication

- `POST /auth/login`
- `POST /auth/logout`
- `POST /auth/refresh`
- `GET /auth/me`

## 3. Projects and milestones

- `GET /projects`
- `POST /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `GET /projects/{project_id}/milestones`
- `POST /projects/{project_id}/milestones`
- `GET /milestones/{milestone_id}`
- `GET /milestones/{milestone_id}/requirements`

## 4. Evidence

- `POST /evidence/uploads/initiate` — authorize upload and return short-lived upload target or upload session.
- `POST /evidence` — finalize submission and create evidence record.
- `GET /evidence`
- `GET /evidence/{evidence_id}`
- `GET /evidence/{evidence_id}/files/{file_id}/access` — issue authorized short-lived access URL.
- `GET /evidence/{evidence_id}/analysis`
- `POST /evidence/{evidence_id}/reanalyze` — privileged, audited action.
- `GET /evidence/{evidence_id}/integrity`
- `GET /evidence/{evidence_id}/history`

Evidence creation should accept project, milestone, optional site, capture method, capture time, coordinates, accuracy, location source, category and notes. The server calculates the hash; client hash is informational only.

## 5. Reviews and corrective actions

- `GET /reviews/queue`
- `POST /evidence/{evidence_id}/reviews`
- `GET /evidence/{evidence_id}/reviews`
- `POST /evidence/{evidence_id}/corrective-actions`
- `PATCH /corrective-actions/{action_id}`
- `POST /evidence/{evidence_id}/resubmissions`

Review payload:
```json
{
  "decision": "correction_requested",
  "reason_code": "INSUFFICIENT_EVIDENCE",
  "comments": "Please submit a wider view and the required measurement."
}
```

## 6. Verification

- `GET /verify/{verification_id}` — public response only if public verification is enabled.
- `POST /evidence/{evidence_id}/integrity-check` — authenticated integrity check.

Public responses should not expose submitter personal details, precise site coordinates, original image URLs or confidential project data unless explicitly authorized.

## 7. AI and knowledge base (internal/admin)

- `GET /ai/models`
- `GET /ai/pipelines`
- `POST /knowledge-documents`
- `GET /knowledge-documents`
- `POST /knowledge-documents/{document_id}/reindex`

These endpoints require elevated permissions.

## 8. HTTP status codes

- `200` successful read/update.
- `201` created.
- `202` accepted for asynchronous processing.
- `400` malformed request.
- `401` unauthenticated.
- `403` unauthorized.
- `404` not found or intentionally concealed.
- `409` state conflict or idempotency conflict.
- `413` payload too large.
- `415` unsupported media type.
- `422` semantic validation error.
- `429` rate limit.
- `500` generic server error.
- `503` dependency unavailable.

## 9. API security

- Validate ownership and scope on every endpoint.
- Apply rate limits.
- Use CSRF protection for cookie-based sessions.
- Validate upload content, not only filename.
- Short-lived signed URLs.
- Avoid leaking whether confidential resources exist.
- Log request IDs, not secrets or file contents.
