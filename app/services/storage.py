from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.utils.settings import settings


def _ensure_local_dir() -> Path:
    p = Path(settings.local_images_dir)
    p.mkdir(parents=True, exist_ok=True)
    return p


async def save_image(file: UploadFile, listing_id: str) -> str:
    """Save an image and return a public URL/path.

    For local storage, returns a URL path under /listings/images/{filename} that the API can serve via StaticFiles.
    """
    filename = f"{listing_id}_{file.filename}"
    if settings.storage_provider == "local":
        folder = _ensure_local_dir()
        target = folder / filename
        content = await file.read()
        target.write_bytes(content)
        return f"/listings/images/{filename}"

    # Placeholder for S3 implementation
    # elif settings.storage_provider == "s3":
    #     ... upload using boto3 and return public URL based on settings.s3_base_url ...

    raise RuntimeError("Unsupported STORAGE_PROVIDER")
