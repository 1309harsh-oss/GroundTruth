from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apps.api.app.core.config import settings
from apps.api.app.core.database import engine, Base
from apps.api.app.api.v1.auth import router as auth_router
from apps.api.app.api.v1.evidence import router as evidence_router

# Initialize database schema tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GroundTruth - Intelligent Infrastructure Evidence Verification API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)

# Initialize Firebase Service
from apps.api.app.services.firebase_service import firebase_service
firebase_service.initialize()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "GroundTruth",
        "version": settings.VERSION,
        "firebase_connected": firebase_service.is_connected
    }

