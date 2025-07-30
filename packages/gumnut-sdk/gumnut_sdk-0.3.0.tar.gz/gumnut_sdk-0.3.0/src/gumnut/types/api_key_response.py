# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["APIKeyResponse"]


class APIKeyResponse(BaseModel):
    id: str

    created_at: datetime

    is_active: bool

    last_used_at: Optional[datetime] = None

    name: Optional[str] = None
