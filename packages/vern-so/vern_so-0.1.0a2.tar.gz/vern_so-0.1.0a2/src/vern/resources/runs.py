# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict

import httpx

from ..types import run_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.run_create_response import RunCreateResponse
from ..types.run_retrieve_response import RunRetrieveResponse

__all__ = ["RunsResource", "AsyncRunsResource"]


class RunsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/vern-so/sdk-python#accessing-raw-response-data-eg-headers
        """
        return RunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/vern-so/sdk-python#with_streaming_response
        """
        return RunsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        task_id: str,
        inputs: Dict[str, object] | NotGiven = NOT_GIVEN,
        profile_id: str | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """
        Executes a task with the provided inputs

        Args:
          task_id: The ID of the task to execute

          inputs: The inputs required for the task

          profile_id: Optional user-specified UID for a profile linked via magic link

          url: An optional URL to be processed by the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/runs",
            body=maybe_transform(
                {
                    "task_id": task_id,
                    "inputs": inputs,
                    "profile_id": profile_id,
                    "url": url,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRetrieveResponse:
        """
        Retrieves the details of a specific task run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/runs/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )


class AsyncRunsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/vern-so/sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/vern-so/sdk-python#with_streaming_response
        """
        return AsyncRunsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        task_id: str,
        inputs: Dict[str, object] | NotGiven = NOT_GIVEN,
        profile_id: str | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunCreateResponse:
        """
        Executes a task with the provided inputs

        Args:
          task_id: The ID of the task to execute

          inputs: The inputs required for the task

          profile_id: Optional user-specified UID for a profile linked via magic link

          url: An optional URL to be processed by the task

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/runs",
            body=await async_maybe_transform(
                {
                    "task_id": task_id,
                    "inputs": inputs,
                    "profile_id": profile_id,
                    "url": url,
                },
                run_create_params.RunCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunCreateResponse,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RunRetrieveResponse:
        """
        Retrieves the details of a specific task run

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/runs/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RunRetrieveResponse,
        )


class RunsResourceWithRawResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.create = to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = to_raw_response_wrapper(
            runs.retrieve,
        )


class AsyncRunsResourceWithRawResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.create = async_to_raw_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            runs.retrieve,
        )


class RunsResourceWithStreamingResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.create = to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            runs.retrieve,
        )


class AsyncRunsResourceWithStreamingResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.create = async_to_streamed_response_wrapper(
            runs.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            runs.retrieve,
        )
