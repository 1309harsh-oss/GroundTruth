from apps.api.app.core.database import SessionLocal, Base, engine
from apps.api.app.models.entities import Organization, User, Project, Site, Milestone
from apps.api.app.core.security import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if org exists
    org = db.query(Organization).filter(Organization.slug == "pwd-state").first()
    if not org:
        org = Organization(
            name="Public Works Department",
            slug="pwd-state",
            status="ACTIVE"
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # Submitter User
    submitter = db.query(User).filter(User.email == "worker@groundtruth.local").first()
    if not submitter:
        submitter = User(
            organization_id=org.id,
            email="worker@groundtruth.local",
            display_name="Site Engineer Ramesh",
            password_hash=get_password_hash("password123"),
            role="SUBMITTER",
            status="ACTIVE"
        )
        db.add(submitter)

    # Reviewer User
    reviewer = db.query(User).filter(User.email == "reviewer@groundtruth.local").first()
    if not reviewer:
        reviewer = User(
            organization_id=org.id,
            email="reviewer@groundtruth.local",
            display_name="Executive Engineer Priya",
            password_hash=get_password_hash("password123"),
            role="REVIEWER",
            status="ACTIVE"
        )
        db.add(reviewer)

    # Admin User
    admin = db.query(User).filter(User.email == "admin@groundtruth.local").first()
    if not admin:
        admin = User(
            organization_id=org.id,
            email="admin@groundtruth.local",
            display_name="System Administrator",
            password_hash=get_password_hash("password123"),
            role="ADMIN",
            status="ACTIVE"
        )
        db.add(admin)

    db.commit()

    # Project & Milestone
    proj = db.query(Project).filter(Project.project_code == "NH-48-EXP").first()
    if not proj:
        proj = Project(
            organization_id=org.id,
            project_code="NH-48-EXP",
            name="National Highway 48 Bridge Expansion",
            description="Four-lane bridge superstructure and deck slab reinforcement",
            status="ACTIVE"
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)

        site = Site(
            project_id=proj.id,
            name="Pillar Pier 12 to 14",
            latitude=28.6139,
            longitude=77.2090,
            geofence_radius_meters=150.0,
            address="Sector 18 Flyover Junction"
        )
        db.add(site)

        m1 = Milestone(
            project_id=proj.id,
            name="Subgrade Compaction & Reinforcement Binding",
            description="Inspection of rebar spacing and concrete pre-pour clearance",
            sequence_number=1,
            status="IN_PROGRESS"
        )
        db.add(m1)
        db.commit()

        # Seed Grounded Specifications for RAG
        from apps.api.app.models.entities import ProjectSpecification
        spec1 = ProjectSpecification(
            project_id=proj.id,
            title="IRC:SP:84 Rebar Binding & Spacing Tolerance",
            document_code="MORTH-SEC-1600",
            section_reference="Clause 1604.3.2",
            category="REBAR_INSPECTION",
            content="Main longitudinal reinforcement bars for deck slab and pier caps must maintain 150mm c/c spacing with 50mm clear concrete cover.",
            numeric_tolerance="+/- 5mm spacing, min 45mm cover"
        )
        spec2 = ProjectSpecification(
            project_id=proj.id,
            title="Surface Water Drainage & Culvert Bed Slope",
            document_code="IRC-SP-42",
            section_reference="Clause 4.1.2",
            category="DRAINAGE_WORKS",
            content="Box culvert precast units must be laid on 150mm lean concrete M15 bedding with a minimum continuous longitudinal fall of 1 in 100.",
            numeric_tolerance="Bed slope tolerance 1:100 to 1:80"
        )
        db.add(spec1)
        db.add(spec2)
        db.commit()
        print("Database seeded successfully with initial project and demo users.")
    else:
        print("Database already contains seed data.")

if __name__ == "__main__":
    seed_db()

