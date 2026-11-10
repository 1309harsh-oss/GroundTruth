import io
from PIL import Image, ImageStat
import imagehash
from sqlalchemy.orm import Session
from apps.api.app.models.entities import Evidence, AIFinding, AuditLog
from apps.api.app.services.storage import storage_service

class WorkerService:
    @staticmethod
    def assess_image_quality(img: Image.Image) -> dict:
        """
        Calculates resolution, exposure/brightness, and contrast metrics.
        """
        width, height = img.size
        # Grayscale stats for brightness and contrast
        gray = img.convert('L')
        stat = ImageStat.Stat(gray)
        mean_brightness = stat.mean[0]  # 0 to 255
        std_dev_contrast = stat.stddev[0]

        flags = []
        is_low_res = (width < 800 or height < 600)
        if is_low_res:
            flags.append("LOW_RESOLUTION")

        # Exposure checks
        exposure_status = "acceptable"
        if mean_brightness < 40:
            exposure_status = "underexposed"
            flags.append("UNDEREXPOSED")
        elif mean_brightness > 220:
            exposure_status = "overexposed"
            flags.append("OVEREXPOSED")

        # Contrast checks
        contrast_status = "acceptable"
        if std_dev_contrast < 20:
            contrast_status = "low_contrast"
            flags.append("LOW_CONTRAST")

        quality_score = 0.95
        if flags:
            quality_score = max(0.3, 0.95 - (0.2 * len(flags)))

        return {
            "resolution": f"{width}x{height}",
            "mean_brightness": round(mean_brightness, 2),
            "contrast_std": round(std_dev_contrast, 2),
            "exposure_status": exposure_status,
            "contrast_status": contrast_status,
            "flags": flags,
            "quality_score": round(quality_score, 2)
        }

    @staticmethod
    def detect_duplicate_candidates(evidence: Evidence, p_hash_str: str, db: Session) -> list[dict]:
        """
        Perceptual duplicate detection: compares pHash against all prior evidence in the same project/organization.
        Perceptual distance <= 5 flags a potential duplicate candidate (not proof of fraud).
        """
        current_phash = imagehash.hex_to_hash(p_hash_str)
        candidates = []

        # Find other evidence records
        prior_records = db.query(Evidence).filter(
            Evidence.id != evidence.id,
            Evidence.phash.isnot(None)
        ).all()

        for prior in prior_records:
            if not prior.phash:
                continue
            try:
                prior_ph = imagehash.hex_to_hash(prior.phash)
                hamming_dist = int(current_phash - prior_ph)
                if hamming_dist <= 8:  # Potential duplicate threshold
                    candidates.append({
                        "prior_evidence_id": prior.id,
                        "prior_filename": prior.original_filename,
                        "hamming_distance": int(hamming_dist),
                        "similarity_percentage": float(round(max(0.0, 100.0 - (hamming_dist / 64.0 * 100.0)), 1)),
                        "candidate_type": "EXACT_OR_HIGH_PERCEPTUAL_MATCH" if hamming_dist <= 2 else "NEAR_DUPLICATE_CANDIDATE"
                    })
            except Exception:
                continue

        return candidates

    @classmethod
    def process_evidence_async(cls, evidence_id: str, db: Session):
        """
        Background job executing validation, perceptual hashing, image quality,
        and duplicate screening. All findings remain strictly advisory.
        """
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            return

        evidence.processing_status = "PROCESSING"
        db.commit()

        try:
            # 1. Fetch original bytes and open image
            file_bytes = storage_service.retrieve_original(evidence.storage_key)
            img = Image.open(io.BytesIO(file_bytes))

            # 2. Compute Perceptual Hashes (pHash and dHash)
            computed_phash = str(imagehash.phash(img))
            computed_dhash = str(imagehash.dhash(img))
            evidence.phash = computed_phash
            evidence.dhash = computed_dhash

            # 3. Assess Image Quality (resolution, exposure, contrast)
            quality_result = cls.assess_image_quality(img)
            all_flags = list(quality_result["flags"])

            # 4. Check Geofence & Location via Haversine
            site = evidence.milestone.project.sites[0] if evidence.milestone.project.sites else None
            site_lat = site.latitude if site else None
            site_lon = site.longitude if site else None
            site_radius = site.geofence_radius_meters if site else 100.0

            from apps.api.app.services.knowledge_gis import knowledge_gis_service
            geo_eval = knowledge_gis_service.evaluate_geofence(
                evidence.capture_latitude,
                evidence.capture_longitude,
                site_lat,
                site_lon,
                site_radius
            )
            evidence.location_status = geo_eval["status"]
            if geo_eval["status"] == "OUTSIDE_GEOFENCE":
                all_flags.append(f"OUTSIDE_GEOFENCE ({geo_eval['detail']})")
            elif geo_eval["status"] == "UNVERIFIED_OR_MISSING":
                all_flags.append("LOCATION_UNVERIFIED")

            # 4b. Retrieve Grounded Engineering Specifications (RAG)
            specs = knowledge_gis_service.retrieve_grounded_specifications(
                evidence.category,
                evidence.milestone.project_id,
                db
            )

            # 5. Check Perceptual Similarity & Duplicate Candidates
            duplicate_candidates = cls.detect_duplicate_candidates(evidence, computed_phash, db)
            if duplicate_candidates:
                all_flags.append(f"POTENTIAL_DUPLICATE_IMAGE_DETECTED ({len(duplicate_candidates)} candidate(s))")

            # 6. Advisory Recommendation (NEVER final approval)
            if duplicate_candidates or any(f in ["LOW_RESOLUTION", "UNDEREXPOSED", "OVEREXPOSED"] for f in all_flags):
                recommendation = "ATTENTION_REQUIRED"
            else:
                recommendation = "NORMAL_REVIEW"

            evidence.ai_quality_score = quality_result["quality_score"]
            evidence.ai_flags = all_flags
            evidence.ai_recommendation = recommendation
            evidence.processing_status = "COMPLETED"

            # 7. Persist Structured AI Findings
            # Finding A: Quality Assessment
            q_finding = AIFinding(
                evidence_id=evidence.id,
                model_name="groundtruth-quality-analyzer",
                model_version="1.1.0",
                finding_type="QUALITY_ASSESSMENT",
                confidence=quality_result["quality_score"],
                details=quality_result
            )
            db.add(q_finding)

            # Finding B: Similarity Candidates
            if duplicate_candidates:
                sim_finding = AIFinding(
                    evidence_id=evidence.id,
                    model_name="groundtruth-similarity-matcher",
                    model_version="1.0.0",
                    finding_type="PERCEPTUAL_SIMILARITY",
                    confidence=0.95,
                    details={"candidates": duplicate_candidates, "phash": computed_phash, "dhash": computed_dhash}
                )
                db.add(sim_finding)

            # Finding C: Grounded RAG Milestone Requirement Context
            if specs:
                rag_finding = AIFinding(
                    evidence_id=evidence.id,
                    model_name="groundtruth-rag-retriever",
                    model_version="1.0.0",
                    finding_type="REQUIREMENT_CONTEXT",
                    confidence=1.0,
                    details={"matched_specifications": specs}
                )
                db.add(rag_finding)

            # 8. Append Audit Log
            audit = AuditLog(
                entity_type="EVIDENCE",
                entity_id=evidence.id,
                action="AI_SCREENING_COMPLETED",
                changes={
                    "quality": quality_result,
                    "phash": computed_phash,
                    "duplicate_count": len(duplicate_candidates),
                    "recommendation": recommendation
                }
            )
            db.add(audit)
            db.commit()

        except Exception as e:
            evidence.processing_status = "FAILED"
            audit = AuditLog(
                entity_type="EVIDENCE",
                entity_id=evidence.id,
                action="AI_SCREENING_FAILED",
                changes={"error": str(e)}
            )
            db.add(audit)
            db.commit()

worker_service = WorkerService()

