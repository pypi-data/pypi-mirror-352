# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["AlbumListParams"]


class AlbumListParams(TypedDict, total=False):
    limit: int

    starting_after_id: Optional[str]
    """Album ID to start listing albums after"""
