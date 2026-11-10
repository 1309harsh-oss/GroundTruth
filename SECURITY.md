# Security, Privacy and Evidence Integrity

## 1. Security objectives

Confidentiality, integrity, availability, accountability and least privilege for evidence and project records.

## 2. Identity and access

- RBAC with organization and project scope.
- Enforce authorization in backend services and database queries.
- Privileged account MFA where feasible.
- Secure password hashing if local passwords are used.
- Short-lived access tokens/sessions and secure refresh handling.
- Session revocation on account disablement.
- Audit role and permission changes.

## 3. Upload security

- Allowlist formats and MIME types.
- Validate magic bytes and successful decoding.
- Limit file size, dimensions and decompression resource usage.
- Generate storage keys; never trust user paths.
- Quarantine before processing where appropriate.
- Malware scanning where available.
- Prevent path traversal and content-type confusion.
- Store originals privately.
- Serve files with safe content disposition and authorization.

## 4. Evidence integrity

- Calculate SHA-256 on server-side original bytes.
- Store hash, algorithm, file size, storage version and timestamp.
- Preserve original bytes and immutable object key.
- Recompute hash during verification.
- Keep derivatives separate from original.
- Use perceptual hashes only for similarity detection.
- Record evidence chain-of-custody events.
- Consider digitally signed server-side manifests for tamper-evident records; this is conventional cryptography, not blockchain.

## 5. Audit logging

Record:
- Evidence creation and access to sensitive files.
- Metadata changes.
- AI run creation and completion.
- Reviewer decisions.
- Corrective actions.
- Role and permission changes.
- Verification attempts.
- Administrative actions.

Protect logs from ordinary update/delete operations. Restrict access and define retention.

## 6. Privacy

- Request camera/location permissions only when needed.
- Explain why location is collected.
- Record location source and accuracy.
- Avoid unnecessary personal information in EXIF retention.
- Apply retention and deletion rules approved by the data owner.
- Redact sensitive data from logs.
- Use private-by-default project and evidence access.
- Public verification must be opt-in and field-limited.

## 7. Threat model

| Threat | Mitigation |
|---|---|
| Reused image | Exact hash + perceptual similarity + reviewer check |
| Altered image | Original preservation, hash verification, provenance checks |
| Spoofed GPS | Accuracy/source labels, geofence anomaly flags, corroboration |
| Unauthorized evidence access | RBAC, scoped queries, signed URLs |
| Malicious upload | File validation, quarantine, scanning, resource limits |
| Insider changes | Append-only audit events, privileged access controls |
| AI prompt injection in OCR/docs | Treat extracted text as untrusted data; isolate instructions |
| Data leakage via public QR | Opaque IDs and strict public response allowlist |
| Model error | Human review, class-specific evaluation, uncertainty |
| Service outage | Backups, queue retries, recovery runbooks |

## 8. Incident response

Define contacts, severity levels, evidence preservation, credential rotation, containment, notification obligations and post-incident review before production use.
