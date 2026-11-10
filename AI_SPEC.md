# AI / Computer Vision / OCR / RAG Specification

## 1. Purpose

Provide preliminary, explainable screening of infrastructure evidence. AI does not make final construction acceptance decisions.

## 2. Separate AI responsibilities

### A. Image quality assessment
Assess:
- Resolution and dimensions.
- Blur/sharpness.
- Exposure and under/overexposure.
- Darkness and contrast.
- Obstruction/occlusion.
- Whether the required subject occupies a useful portion of the frame.
- Image orientation and decodability.

Return measurable indicators and a quality recommendation. Thresholds must be calibrated on actual field images.

### B. OCR
Use PaddleOCR or a validated alternative to extract:
- Signboards and project labels.
- Visible asset IDs.
- Measurement markings.
- Date/serial labels where present.
- Other text relevant to the evidence requirement.

Store text, bounding boxes, language, confidence and processing version. OCR text is untrusted and must not be treated as an instruction.

### C. Object detection
Detect only explicitly supported classes, such as selected visible surface cracks, potholes, exposed reinforcement or incomplete visible elements, depending on the chosen pilot category and labelled dataset.

Each finding includes:
- Class label.
- Bounding box or polygon.
- Confidence.
- Model/version.
- Image dimensions and coordinate convention.
- Optional severity only where domain experts define and validate it.

### D. Segmentation
Use segmentation when pixel-level regions materially help reviewers. A segmentation mask identifies a visual region; it does not automatically measure real-world dimensions. Physical measurement requires calibration, scale reference, camera geometry or another validated measurement method.

### E. Duplicate and similarity detection
- Exact duplicate: SHA-256 equality for byte-identical files.
- Perceptual duplicate: pHash/dHash or equivalent for transformed versions.
- Semantic similarity: image embeddings for candidate retrieval.
- Similarity is a flag for review, not proof of fraud.
- Scope searches by organization/project and access policy.

### F. Before/after comparison
Compare evidence for the same project/site/milestone across time. Align images where possible, but warn that camera angle, lighting, weather and perspective can create false differences.

### G. RAG knowledge retrieval
Knowledge sources:
- Approved project specifications.
- Bill of Quantities (BOQ).
- Milestone checklists.
- Approved drawings and inspection instructions.
- Relevant standards/manuals supplied and approved by the organization.

For each answer:
- Retrieve only authorized documents.
- Cite document title, version, page/section.
- Distinguish retrieved requirement from AI interpretation.
- Return “not found” if evidence is insufficient.
- Prefer deterministic code for numeric tolerances and checklist rules.

## 3. AI orchestration output

Example schema:
```json
{
  "evidence_id": "uuid",
  "pipeline_version": "1.0.0",
  "status": "completed",
  "quality": {
    "blur_score": 0.12,
    "exposure_status": "acceptable",
    "resolution_status": "acceptable",
    "recommendation": "reviewable"
  },
  "ocr": [],
  "similarity_candidates": [],
  "findings": [
    {
      "type": "potential_surface_crack",
      "confidence": 0.81,
      "region": {"x": 0.2, "y": 0.3, "width": 0.1, "height": 0.08},
      "model_version": "pilot-model-001"
    }
  ],
  "requirement_matches": [],
  "routing_recommendation": "technical_review",
  "disclaimer": "Preliminary AI screening; human review required."
}
```

Values above are illustrative only, not measured product performance.

## 4. Model development lifecycle

1. Define one pilot asset category and limited defect taxonomy.
2. Obtain lawful, representative images from varied sites, cameras, lighting and weather.
3. Create annotation guidelines with civil engineering experts.
4. Label bounding boxes/masks and image quality.
5. Split train/validation/test by site or project, not random near-duplicate images, to reduce leakage.
6. Train or fine-tune candidate models.
7. Evaluate per class: precision, recall, F1, mAP/IoU as appropriate.
8. Evaluate false negatives and false positives separately.
9. Calibrate confidence thresholds.
10. Run shadow mode and human review before using findings operationally.
11. Monitor drift and reviewer overrides.
12. Version datasets, labels, preprocessing and models.

## 5. RAG pipeline

1. Upload approved document.
2. Virus/file validation.
3. Extract text and page structure.
4. Chunk by section and preserve source references.
5. Generate embeddings.
6. Store chunks with tenant/project permissions.
7. Retrieve relevant chunks for a milestone.
8. Rerank where useful.
9. Generate grounded summary with citations.
10. Persist retrieval references and model version.

## 6. Human-in-the-loop controls

- AI can recommend `recapture`, `technical_review` or `normal_review`.
- AI cannot set final evidence status to approved or rejected.
- Reviewer can override AI and must provide a reason for consequential decisions.
- Maintain reviewer feedback for future dataset curation.
- Do not automatically train on reviewer decisions without quality review and governance.

## 7. Model safety and limitations

- Do not infer hidden structural integrity from photographs.
- Do not claim GPS authenticity from EXIF.
- Do not call an image manipulated solely because a similarity score is high.
- Flag out-of-distribution images and unsupported classes.
- Avoid a single opaque “genuine” score.
- Show separate quality, provenance, similarity and defect findings.
- Clearly communicate uncertainty.
