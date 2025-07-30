# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import AsyncResultRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAsyncResults:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: SampleHealthcare) -> None:
        async_result = client.v2.async_results.retrieve(
            "asyncResultId",
        )
        assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: SampleHealthcare) -> None:
        response = client.v2.async_results.with_raw_response.retrieve(
            "asyncResultId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_result = response.parse()
        assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: SampleHealthcare) -> None:
        with client.v2.async_results.with_streaming_response.retrieve(
            "asyncResultId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_result = response.parse()
            assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `async_result_id` but received ''"):
            client.v2.async_results.with_raw_response.retrieve(
                "",
            )


class TestAsyncAsyncResults:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        async_result = await async_client.v2.async_results.retrieve(
            "asyncResultId",
        )
        assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.async_results.with_raw_response.retrieve(
            "asyncResultId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        async_result = await response.parse()
        assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.async_results.with_streaming_response.retrieve(
            "asyncResultId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            async_result = await response.parse()
            assert_matches_type(AsyncResultRetrieveResponse, async_result, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `async_result_id` but received ''"):
            await async_client.v2.async_results.with_raw_response.retrieve(
                "",
            )
