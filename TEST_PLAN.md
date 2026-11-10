# Test Plan

## 1. Test levels

- Unit tests: domain services, validators, hashing, state transitions.
- Integration tests: database, object storage, queue, API and AI adapters.
- Contract tests: request/response schemas and API compatibility.
- End-to-end tests: submitter, reviewer and verifier journeys.
- Security tests: authorization, upload abuse, injection and data exposure.
- AI evaluation: labelled holdout datasets and field-condition slices.
- Performance tests: upload, dashboard, queue throughput and inference.
- Recovery tests: backup restore, queue retry and dependency outage.

## 2. Critical test scenarios

### Evidence upload
- Valid JPEG/PNG accepted.
- Unsupported format rejected.
- Spoofed extension with invalid file signature rejected.
- Oversized file rejected.
- Corrupt image rejected.
- Unauthorized project submission denied.
- Duplicate request does not create duplicate evidence when idempotency key is reused.
- Original bytes preserved exactly.

### SHA-256
- Same bytes produce same digest.
- One-byte change produces a different digest.
- Stored original hash matches downloaded original.
- Derivative hash is not confused with original hash.
- Hash mismatch triggers alert and safe status.

### Metadata and geospatial
- GPS absent is represented as unavailable.
- GPS accuracy is retained.
- Invalid coordinates rejected.
- Geofence check accounts for configured tolerance.
- EXIF time and server receipt time remain distinct.
- Manual metadata is labelled as manually entered.

### AI
- Quality checks return expected schema.
- OCR stores text and bounding boxes.
- Duplicate candidate is flagged but not auto-rejected.
- Unsupported model class returns no finding rather than hallucinating a class.
- Inference failure is retryable.
- Model version is persisted.
- Confidence threshold behavior is tested per class.
- Out-of-distribution samples are flagged or routed conservatively.

### Review
- Only assigned/authorized reviewers can decide.
- Decision reason is recorded.
- AI cannot approve/reject.
- Rejected record remains in history.
- Resubmission links to prior evidence.
- Reviewer override is audited.

### Verification
- Authorized verifier sees permitted details.
- Public verifier sees only allowlisted details.
- Invalid/expired ID returns safe response.
- Hash match does not display a claim of capture authenticity.

## 3. AI metrics

Evaluate per class and dataset slice:
- Precision, recall, F1.
- Confusion matrix.
- mAP for detection.
- IoU/Dice for segmentation.
- False positive and false negative rates.
- Calibration metrics if confidence is presented probabilistically.
- Performance by site, camera, lighting, weather and capture distance.

Do not release a model based only on aggregate accuracy.

## 4. Release gates

- No unresolved critical/high security issue.
- All critical user journeys pass.
- Authorization tests pass.
- Backup and restore tested.
- Model evaluation reviewed by domain expert.
- Known limitations documented.
- Reviewer workflow operational.
- Monitoring and error reporting enabled.
