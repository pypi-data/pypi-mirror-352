# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SearchSearchParams"]


class SearchSearchParams(TypedDict, total=False):
    query: Required[str]
    """The text query to search for"""

    limit: int
    """Number of results per page"""

    page: int
    """Page number"""

    threshold: float
    """Similarity threshold (lower means more similar)"""
