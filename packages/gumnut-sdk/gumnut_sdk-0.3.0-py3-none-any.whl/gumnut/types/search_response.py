# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .asset_response import AssetResponse

__all__ = ["SearchResponse", "Data"]


class Data(BaseModel):
    asset: AssetResponse

    distance: float


class SearchResponse(BaseModel):
    data: List[Data]
