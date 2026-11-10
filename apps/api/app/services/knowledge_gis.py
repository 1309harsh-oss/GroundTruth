import math
from sqlalchemy.orm import Session
from apps.api.app.models.entities import ProjectSpecification, Evidence, AIFinding

class KnowledgeGISService:
    @staticmethod
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate accurate spherical distance in meters between two coordinates."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @classmethod
    def evaluate_geofence(cls, evidence_lat: float, evidence_lon: float, site_lat: float, site_lon: float, radius_meters: float) -> dict:
        """
        Evaluates capture coordinate against site centroid and boundary tolerance.
        """
        if evidence_lat is None or evidence_lon is None or site_lat is None or site_lon is None:
            return {
                "status": "UNVERIFIED_OR_MISSING",
                "distance_meters": None,
                "in_geofence": False,
                "detail": "GPS metadata absent or uncalibrated"
            }

        dist_meters = cls.haversine_distance_meters(evidence_lat, evidence_lon, site_lat, site_lon)
        in_fence = (dist_meters <= radius_meters)

        return {
            "status": "VERIFIED_IN_GEOFENCE" if in_fence else "OUTSIDE_GEOFENCE",
            "distance_meters": round(dist_meters, 2),
            "radius_meters": radius_meters,
            "in_geofence": in_fence,
            "detail": f"Distance from site center: {round(dist_meters, 1)}m (Tolerance radius: {radius_meters}m)"
        }

    @staticmethod
    def retrieve_grounded_specifications(evidence_category: str, project_id: str, db: Session) -> list[dict]:
        """
        RAG / Knowledge retrieval for relevant engineering specifications, tolerances, and BOQ rules.
        """
        specs = db.query(ProjectSpecification).filter(
            ProjectSpecification.project_id == project_id
        ).all()

        matched = []
        cat_lower = evidence_category.lower()

        for s in specs:
            # Match by category or keyword
            if s.category.lower() in cat_lower or any(kw in cat_lower for kw in s.category.lower().split('_')):
                matched.append({
                    "id": s.id,
                    "title": s.title,
                    "document_code": s.document_code,
                    "section_reference": s.section_reference,
                    "requirement_text": s.content,
                    "numeric_tolerance": s.numeric_tolerance
                })

        return matched

knowledge_gis_service = KnowledgeGISService()

