# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date, datetime

from .._models import BaseModel

__all__ = ["PersonResponse"]


class PersonResponse(BaseModel):
    id: str

    created_at: datetime

    is_favorite: bool

    is_hidden: bool

    updated_at: datetime

    birth_date: Optional[date] = None

    name: Optional[str] = None

    thumbnail_face_id: Optional[str] = None

    thumbnail_face_url: Optional[str] = None
