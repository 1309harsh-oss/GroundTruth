import os
import hashlib
import uuid
from pathlib import Path
from fastapi import HTTPException
from apps.api.app.core.config import settings

class StorageService:
    def __init__(self, root_dir: str = settings.STORAGE_LOCAL_ROOT):
        self.root_dir = Path(root_dir)
        self.originals_dir = self.root_dir / "originals"
        self.derivatives_dir = self.root_dir / "derivatives"
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.derivatives_dir.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, content_bytes: bytes) -> str:
        """Calculate cryptographically secure SHA-256 digest of original bytes."""
        hasher = hashlib.sha256()
        hasher.update(content_bytes)
        return hasher.hexdigest()

    def store_original(self, content_bytes: bytes, original_extension: str) -> tuple[str, str, int]:
        """
        Stores immutable original file under generated UUID key.
        Returns (storage_key, sha256_hash, byte_length).
        """
        sha256_hash = self.compute_sha256(content_bytes)
        ext = original_extension if original_extension.startswith(".") else f".{original_extension}"
        storage_key = f"{uuid.uuid4()}{ext}"
        target_path = self.originals_dir / storage_key

        # Guard against path traversal
        if not target_path.resolve().is_relative_to(self.originals_dir.resolve()):
            raise HTTPException(status_code=400, detail="Invalid storage path")

        # Save immutable bytes
        with open(target_path, "wb") as f:
            f.write(content_bytes)

        return storage_key, sha256_hash, len(content_bytes)

    def retrieve_original(self, storage_key: str) -> bytes:
        """Retrieves raw original bytes for download or integrity checks."""
        target_path = self.originals_dir / storage_key
        if not target_path.exists():
            raise FileNotFoundError(f"Storage file {storage_key} not found")
        with open(target_path, "rb") as f:
            return f.read()

    def verify_file_integrity(self, storage_key: str, recorded_sha256: str) -> tuple[bool, str]:
        """
        Recomputes hash from physical bytes on disk/storage and matches against database record.
        """
        try:
            raw_bytes = self.retrieve_original(storage_key)
            current_hash = self.compute_sha256(raw_bytes)
            is_valid = (current_hash.lower() == recorded_sha256.lower())
            return is_valid, current_hash
        except FileNotFoundError:
            return False, "FILE_NOT_FOUND"

storage_service = StorageService()

