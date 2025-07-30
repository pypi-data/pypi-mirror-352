# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AssetResponse", "Exif"]


class Exif(BaseModel):
    altitude: Optional[float] = None

    auto_stack_id: Optional[str] = None

    city: Optional[str] = None

    country: Optional[str] = None

    description: Optional[str] = None

    digitized_datetime: Optional[datetime] = None

    exposure_bias: Optional[float] = None

    exposure_time: Optional[float] = None

    f_number: Optional[float] = None

    focal_length: Optional[float] = None

    fps: Optional[float] = None

    iso: Optional[int] = None

    latitude: Optional[float] = None

    lens_model: Optional[str] = None

    live_photo_cid: Optional[str] = None

    longitude: Optional[float] = None

    make: Optional[str] = None

    model: Optional[str] = None

    modified_datetime: Optional[datetime] = None

    orientation: Optional[int] = None

    original_datetime: Optional[datetime] = None

    profile_description: Optional[str] = None

    projection_type: Optional[str] = None

    rating: Optional[int] = None

    state: Optional[str] = None


class AssetResponse(BaseModel):
    id: str

    checksum: str

    created_at: datetime

    device_asset_id: str

    device_id: str

    file_created_at: datetime

    file_modified_at: datetime

    local_datetime: datetime

    mime_type: str

    original_file_name: str

    updated_at: datetime

    download_url: Optional[str] = None

    exif: Optional[Exif] = None

    metrics: Optional[Dict[str, Optional[float]]] = None

    thumbnail_url: Optional[str] = None
