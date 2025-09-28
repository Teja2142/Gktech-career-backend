import os
import io
import uuid
from typing import Optional
from .config import settings
from minio import Minio
from minio.error import S3Error

# Cached client and initialized-buckets set to avoid repeated round-trips
_MINIO_CLIENT: Optional[Minio] = None
_INITIALIZED_BUCKETS = set()


def _get_minio_client() -> Minio:
    """Constructs a MinIO client using settings.

    Expects these settings to be set in environment or `app.config`:
    - MINIO_ENDPOINT
    - MINIO_ACCESS_KEY
    - MINIO_SECRET_KEY
    - MINIO_SECURE (optional)
    """
    endpoint = getattr(settings, "MINIO_ENDPOINT", None) or os.environ.get("MINIO_ENDPOINT")
    access_key = getattr(settings, "MINIO_ACCESS_KEY", None) or os.environ.get("MINIO_ACCESS_KEY")
    secret_key = getattr(settings, "MINIO_SECRET_KEY", None) or os.environ.get("MINIO_SECRET_KEY")
    secure = getattr(settings, "MINIO_SECURE", None)
    # if secure is None:
    #     secure = os.environ.get("MINIO_SECURE", "false").lower() in ("1", "true", "yes")
    secure = False  # For local MinIO without TLS
    

    if not endpoint or not access_key or not secret_key:
        raise RuntimeError("MinIO configuration missing: set MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY")

    global _MINIO_CLIENT
    if _MINIO_CLIENT is None:
        _MINIO_CLIENT = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    return _MINIO_CLIENT


def upload_resume_to_minio(file_bytes: bytes, filename: str, bucket_name: Optional[str] = None) -> str:
    """Uploads resume bytes to a MinIO bucket and returns the object URL/path.

    If `bucket_name` is not provided, uses `MINIO_BUCKET` from settings or env.
    The object key will be stored under `resumes/{uuid}_{filename}`.
    """
    client = _get_minio_client()
    bucket = bucket_name or getattr(settings, "MINIO_BUCKET", None) or os.environ.get("MINIO_BUCKET")
    if not bucket:
        raise RuntimeError("MinIO bucket not configured (MINIO_BUCKET)")

    # ensure bucket exists (do this once per bucket to avoid a round-trip each upload)
    try:
        if bucket not in _INITIALIZED_BUCKETS:
            found = client.bucket_exists(bucket)
            if not found:
                client.make_bucket(bucket)
            _INITIALIZED_BUCKETS.add(bucket)
    except S3Error as exc:
        raise RuntimeError(f"MinIO bucket error: {exc}")

    key = f"resumes/{uuid.uuid4().hex}_{filename}"

    try:
        # MinIO expects a file-like object; wrap bytes in BytesIO so it has a .read()
        data_stream = io.BytesIO(file_bytes)
        client.put_object(bucket, key, data=data_stream, length=len(file_bytes), content_type="application/octet-stream")
    except S3Error as exc:
        raise RuntimeError(f"Failed to upload to MinIO: {exc}")

    # Construct a URL — this may be a presigned URL in some setups; return the internal path
    endpoint = getattr(settings, "MINIO_ENDPOINT", None) or os.environ.get("MINIO_ENDPOINT")
    secure = getattr(settings, "MINIO_SECURE", None)
    if secure is None:
        secure = os.environ.get("MINIO_SECURE", "false").lower() in ("1", "true", "yes")
    scheme = "https" if secure else "http"

    return f"{scheme}://{endpoint}/{bucket}/{key}"
