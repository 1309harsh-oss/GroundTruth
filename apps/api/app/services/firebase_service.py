import os
import json
import logging
from typing import Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self._db = None
        self._initialized = False

    def initialize(self, service_account_path: Optional[str] = None):
        """
        Initializes Firebase Admin SDK using service account JSON if provided.
        Otherwise falls back to graceful mock/offline mode without breaking the application.
        """
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            if not firebase_admin._apps:
                creds_path = service_account_path or os.getenv("FIREBASE_CREDENTIALS_PATH")
                if creds_path and Path(creds_path).exists():
                    cred = credentials.Certificate(creds_path)
                    firebase_admin.initialize_app(cred)
                    self._db = firestore.client()
                    self._initialized = True
                    logger.info("Firebase Firestore initialized successfully with credentials.")
                else:
                    logger.warning("No Firebase credentials file found. Running in offline/hybrid fallback mode.")
            else:
                from firebase_admin import firestore
                self._db = firestore.client()
                self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            self._initialized = False

    @property
    def is_connected(self) -> bool:
        return self._initialized and self._db is not None

    def sync_evidence(self, evidence_data: dict[str, Any]) -> bool:
        """
        Syncs an evidence document to Firebase Cloud Firestore.
        """
        if not self.is_connected:
            return False
        try:
            ev_id = evidence_data.get("id")
            if not ev_id:
                return False
            self._db.collection("evidence").document(str(ev_id)).set(evidence_data, merge=True)
            return True
        except Exception as e:
            logger.error(f"Error syncing evidence to Firestore: {e}")
            return False

    def sync_audit_log(self, audit_data: dict[str, Any]) -> bool:
        """
        Syncs an audit event to Firebase Cloud Firestore append-only collection.
        """
        if not self.is_connected:
            return False
        try:
            log_id = audit_data.get("id")
            if log_id:
                self._db.collection("audit_logs").document(str(log_id)).set(audit_data)
            else:
                self._db.collection("audit_logs").add(audit_data)
            return True
        except Exception as e:
            logger.error(f"Error syncing audit event to Firestore: {e}")
            return False

firebase_service = FirebaseService()

