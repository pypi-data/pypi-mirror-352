# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    LedgerNewOrderResponse,
    LedgerClaimPaymentResponse,
    LedgerOrderWriteoffResponse,
    LedgerPatientPaymentResponse,
    LedgerClaimAdjustmentResponse,
    LedgerPatientAdjustmentResponse,
    LedgerInstitutionPaymentResponse,
    LedgerInstitutionAdjustmentResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLedger:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_claim_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_claim_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_claim_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_claim_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_claim_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_claim_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_institution_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_institution_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_institution_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_institution_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_institution_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_institution_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_new_order(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_new_order_with_all_params(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
            claim_id="claimId",
            institution_id="institutionId",
            insurance_id="insuranceId",
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_new_order(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_new_order(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_order_writeoff(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_order_writeoff(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_order_writeoff(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_patient_adjustment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_patient_adjustment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_patient_adjustment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_patient_payment(self, client: SampleHealthcare) -> None:
        ledger = client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_patient_payment(self, client: SampleHealthcare) -> None:
        response = client.v2.ledger.with_raw_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = response.parse()
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_patient_payment(self, client: SampleHealthcare) -> None:
        with client.v2.ledger.with_streaming_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = response.parse()
            assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLedger:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_claim_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.claim_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerClaimAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        )
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_claim_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.claim_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            insurance_id="insuranceId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerClaimPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_institution_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.institution_adjustment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerInstitutionAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        )
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_institution_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.institution_payment(
            amount_usd_cents=0,
            claim_id="claimId",
            ik="ik",
            institution_id="institutionId",
            order_id="orderId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerInstitutionPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_new_order_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
            claim_id="claimId",
            institution_id="institutionId",
            insurance_id="insuranceId",
        )
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_new_order(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.new_order(
            claim_amount_usd_cents=0,
            institution_amount_usd_cents=0,
            order_id="orderId",
            patient_amount_usd_cents=0,
            patient_id="patientId",
            unallocated_amount_usd_cents=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerNewOrderResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_order_writeoff(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.order_writeoff(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerOrderWriteoffResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_patient_adjustment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.patient_adjustment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
            reason="reason",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerPatientAdjustmentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        ledger = await async_client.v2.ledger.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        )
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.ledger.with_raw_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        ledger = await response.parse()
        assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_patient_payment(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.ledger.with_streaming_response.patient_payment(
            amount_usd_cents=0,
            ik="ik",
            order_id="orderId",
            patient_id="patientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            ledger = await response.parse()
            assert_matches_type(LedgerPatientPaymentResponse, ledger, path=["response"])

        assert cast(Any, response.is_closed) is True
