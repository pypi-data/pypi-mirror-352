# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from photos import Photos, AsyncPhotos
from tests.utils import assert_matches_type
from photos.types import SearchResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search(self, client: Photos) -> None:
        search = client.search.search(
            query="query",
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_with_all_params(self, client: Photos) -> None:
        search = client.search.search(
            query="query",
            limit=1,
            page=1,
            threshold=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search(self, client: Photos) -> None:
        response = client.search.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search(self, client: Photos) -> None:
        with client.search.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSearch:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search(self, async_client: AsyncPhotos) -> None:
        search = await async_client.search.search(
            query="query",
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncPhotos) -> None:
        search = await async_client.search.search(
            query="query",
            limit=1,
            page=1,
            threshold=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncPhotos) -> None:
        response = await async_client.search.with_raw_response.search(
            query="query",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncPhotos) -> None:
        async with async_client.search.with_streaming_response.search(
            query="query",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True
