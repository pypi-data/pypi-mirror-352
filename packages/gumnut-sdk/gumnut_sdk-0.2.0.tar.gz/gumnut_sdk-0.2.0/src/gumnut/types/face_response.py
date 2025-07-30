# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["FaceResponse"]


class FaceResponse(BaseModel):
    id: str

    asset_id: str

    bounding_box: Dict[str, int]

    created_at: datetime

    updated_at: datetime

    person_id: Optional[str] = None

    thumbnail_url: Optional[str] = None

    timestamp_ms: Optional[int] = None
