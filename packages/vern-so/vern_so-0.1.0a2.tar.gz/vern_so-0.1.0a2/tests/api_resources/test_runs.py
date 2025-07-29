# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from vern import Vern, AsyncVern
from vern.types import RunCreateResponse, RunRetrieveResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRuns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create(self, client: Vern) -> None:
        run = client.runs.create(
            task_id="task_123456",
        )
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_with_all_params(self, client: Vern) -> None:
        run = client.runs.create(
            task_id="task_123456",
            inputs={
                "prompt": "bar",
                "text": "bar",
            },
            profile_id="profileId",
            url="https://example.com",
        )
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create(self, client: Vern) -> None:
        response = client.runs.with_raw_response.create(
            task_id="task_123456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create(self, client: Vern) -> None:
        with client.runs.with_streaming_response.create(
            task_id="task_123456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunCreateResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve(self, client: Vern) -> None:
        run = client.runs.retrieve(
            "id",
        )
        assert_matches_type(RunRetrieveResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve(self, client: Vern) -> None:
        response = client.runs.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunRetrieveResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve(self, client: Vern) -> None:
        with client.runs.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunRetrieveResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve(self, client: Vern) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.runs.with_raw_response.retrieve(
                "",
            )


class TestAsyncRuns:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create(self, async_client: AsyncVern) -> None:
        run = await async_client.runs.create(
            task_id="task_123456",
        )
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncVern) -> None:
        run = await async_client.runs.create(
            task_id="task_123456",
            inputs={
                "prompt": "bar",
                "text": "bar",
            },
            profile_id="profileId",
            url="https://example.com",
        )
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncVern) -> None:
        response = await async_client.runs.with_raw_response.create(
            task_id="task_123456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunCreateResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncVern) -> None:
        async with async_client.runs.with_streaming_response.create(
            task_id="task_123456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunCreateResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncVern) -> None:
        run = await async_client.runs.retrieve(
            "id",
        )
        assert_matches_type(RunRetrieveResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncVern) -> None:
        response = await async_client.runs.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunRetrieveResponse, run, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncVern) -> None:
        async with async_client.runs.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunRetrieveResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncVern) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.runs.with_raw_response.retrieve(
                "",
            )
