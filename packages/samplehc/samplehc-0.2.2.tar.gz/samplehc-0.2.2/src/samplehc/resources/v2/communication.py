# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ...types.v2 import communication_send_fax_params, communication_send_email_params
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.v2.communication_send_fax_response import CommunicationSendFaxResponse

__all__ = ["CommunicationResource", "AsyncCommunicationResource"]


class CommunicationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CommunicationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return CommunicationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CommunicationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return CommunicationResourceWithStreamingResponse(self)

    def send_email(
        self,
        *,
        body: str,
        subject: str,
        to: str,
        attachments: Iterable[communication_send_email_params.Attachment] | NotGiven = NOT_GIVEN,
        enable_encryption: bool | NotGiven = NOT_GIVEN,
        zip_attachments: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Processes and dispatches an email.

        Supports plain text and encrypted emails.
        Attachments can be provided by ID, optionally zipped together before sending.
        Encrypted emails are stored and a notification link is sent.

        Args:
          body: The main content/body of the email

          subject: The subject line of the email

          to: The email address of the recipient

          attachments: Optional array of file attachment IDs to include with the email

          enable_encryption: Whether to encrypt the email content and send a secure link instead

          zip_attachments: Whether to compress all attachments into a single zip file before sending

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/communication/send-email",
            body=maybe_transform(
                {
                    "body": body,
                    "subject": subject,
                    "to": to,
                    "attachments": attachments,
                    "enable_encryption": enable_encryption,
                    "zip_attachments": zip_attachments,
                },
                communication_send_email_params.CommunicationSendEmailParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def send_fax(
        self,
        *,
        document: communication_send_fax_params.Document,
        to: str,
        batch_delay_seconds: str | NotGiven = NOT_GIVEN,
        enable_batch_collision_avoidance: bool | NotGiven = NOT_GIVEN,
        enable_batch_delay: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommunicationSendFaxResponse:
        """Initiates an asynchronous fax sending process.

        Returns an async result ID that
        can be used to track the status of the fax transmission.

        Args:
          document: The document to be sent via fax

          to: The fax number to send the document to

          batch_delay_seconds: The delay between each batch of faxes in seconds, only used if enableBatchDelay
              is true, defaults to 60 seconds

          enable_batch_collision_avoidance: Recommended for high-volume fax operations or when sending to recipients who may
              receive multiple faxes simultaneously. Prevents transmission failures by
              automatically queuing your fax when another transmission to the same number is
              already in progress. Your fax will wait and automatically send once the line is
              clear, ensuring reliable delivery without manual intervention.

          enable_batch_delay: If enabled, the fax will be sent in batches according to the specified batch
              delay timing.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v2/communication/send-fax",
            body=maybe_transform(
                {
                    "document": document,
                    "to": to,
                    "batch_delay_seconds": batch_delay_seconds,
                    "enable_batch_collision_avoidance": enable_batch_collision_avoidance,
                    "enable_batch_delay": enable_batch_delay,
                },
                communication_send_fax_params.CommunicationSendFaxParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommunicationSendFaxResponse,
        )


class AsyncCommunicationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCommunicationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCommunicationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCommunicationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncCommunicationResourceWithStreamingResponse(self)

    async def send_email(
        self,
        *,
        body: str,
        subject: str,
        to: str,
        attachments: Iterable[communication_send_email_params.Attachment] | NotGiven = NOT_GIVEN,
        enable_encryption: bool | NotGiven = NOT_GIVEN,
        zip_attachments: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Processes and dispatches an email.

        Supports plain text and encrypted emails.
        Attachments can be provided by ID, optionally zipped together before sending.
        Encrypted emails are stored and a notification link is sent.

        Args:
          body: The main content/body of the email

          subject: The subject line of the email

          to: The email address of the recipient

          attachments: Optional array of file attachment IDs to include with the email

          enable_encryption: Whether to encrypt the email content and send a secure link instead

          zip_attachments: Whether to compress all attachments into a single zip file before sending

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/communication/send-email",
            body=await async_maybe_transform(
                {
                    "body": body,
                    "subject": subject,
                    "to": to,
                    "attachments": attachments,
                    "enable_encryption": enable_encryption,
                    "zip_attachments": zip_attachments,
                },
                communication_send_email_params.CommunicationSendEmailParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def send_fax(
        self,
        *,
        document: communication_send_fax_params.Document,
        to: str,
        batch_delay_seconds: str | NotGiven = NOT_GIVEN,
        enable_batch_collision_avoidance: bool | NotGiven = NOT_GIVEN,
        enable_batch_delay: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CommunicationSendFaxResponse:
        """Initiates an asynchronous fax sending process.

        Returns an async result ID that
        can be used to track the status of the fax transmission.

        Args:
          document: The document to be sent via fax

          to: The fax number to send the document to

          batch_delay_seconds: The delay between each batch of faxes in seconds, only used if enableBatchDelay
              is true, defaults to 60 seconds

          enable_batch_collision_avoidance: Recommended for high-volume fax operations or when sending to recipients who may
              receive multiple faxes simultaneously. Prevents transmission failures by
              automatically queuing your fax when another transmission to the same number is
              already in progress. Your fax will wait and automatically send once the line is
              clear, ensuring reliable delivery without manual intervention.

          enable_batch_delay: If enabled, the fax will be sent in batches according to the specified batch
              delay timing.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v2/communication/send-fax",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "to": to,
                    "batch_delay_seconds": batch_delay_seconds,
                    "enable_batch_collision_avoidance": enable_batch_collision_avoidance,
                    "enable_batch_delay": enable_batch_delay,
                },
                communication_send_fax_params.CommunicationSendFaxParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CommunicationSendFaxResponse,
        )


class CommunicationResourceWithRawResponse:
    def __init__(self, communication: CommunicationResource) -> None:
        self._communication = communication

        self.send_email = to_raw_response_wrapper(
            communication.send_email,
        )
        self.send_fax = to_raw_response_wrapper(
            communication.send_fax,
        )


class AsyncCommunicationResourceWithRawResponse:
    def __init__(self, communication: AsyncCommunicationResource) -> None:
        self._communication = communication

        self.send_email = async_to_raw_response_wrapper(
            communication.send_email,
        )
        self.send_fax = async_to_raw_response_wrapper(
            communication.send_fax,
        )


class CommunicationResourceWithStreamingResponse:
    def __init__(self, communication: CommunicationResource) -> None:
        self._communication = communication

        self.send_email = to_streamed_response_wrapper(
            communication.send_email,
        )
        self.send_fax = to_streamed_response_wrapper(
            communication.send_fax,
        )


class AsyncCommunicationResourceWithStreamingResponse:
    def __init__(self, communication: AsyncCommunicationResource) -> None:
        self._communication = communication

        self.send_email = async_to_streamed_response_wrapper(
            communication.send_email,
        )
        self.send_fax = async_to_streamed_response_wrapper(
            communication.send_fax,
        )
