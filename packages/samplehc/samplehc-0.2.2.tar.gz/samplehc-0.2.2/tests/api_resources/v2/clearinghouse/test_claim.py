# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.clearinghouse import ClaimSubmitResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClaim:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_status(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_status(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_status(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_retrieve_status(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_submit(self, client: SampleHealthcare) -> None:
        claim = client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_submit(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.claim.with_raw_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_submit(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.claim.with_streaming_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClaim:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.retrieve_status(
            "claimId",
        )
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
            "claimId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(object, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.retrieve_status(
            "claimId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(object, claim, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `claim_id` but received ''"):
            await async_client.v2.clearinghouse.claim.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_submit(self, async_client: AsyncSampleHealthcare) -> None:
        claim = await async_client.v2.clearinghouse.claim.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.claim.with_raw_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        claim = await response.parse()
        assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.claim.with_streaming_response.submit(
            claim_information={
                "benefits_assignment_certification_indicator": "benefitsAssignmentCertificationIndicator",
                "claim_charge_amount": "claimChargeAmount",
                "claim_code_information": {
                    "admission_source_code": "admissionSourceCode",
                    "admission_type_code": "admissionTypeCode",
                    "patient_status_code": "patientStatusCode",
                },
                "claim_date_information": {
                    "admission_date_and_hour": "admissionDateAndHour",
                    "statement_begin_date": "statementBeginDate",
                    "statement_end_date": "statementEndDate",
                },
                "claim_filing_code": "claimFilingCode",
                "claim_frequency_code": "claimFrequencyCode",
                "place_of_service_code": "placeOfServiceCode",
                "plan_participation_code": "planParticipationCode",
                "principal_diagnosis": {"principal_diagnosis_code": "principalDiagnosisCode"},
                "release_information_code": "releaseInformationCode",
                "service_lines": [
                    {
                        "institutional_service": {
                            "line_item_charge_amount": "lineItemChargeAmount",
                            "procedure_code": "procedureCode",
                            "service_line_revenue_code": "serviceLineRevenueCode",
                        },
                        "service_date": "serviceDate",
                    }
                ],
            },
            idempotency_key="idempotencyKey",
            is_testing=True,
            providers=[
                {
                    "contact_information": {"name": "name"},
                    "npi": "npi",
                    "provider_type": "providerType",
                }
            ],
            receiver={"organization_name": "organizationName"},
            submitter={
                "contact_information": {
                    "name": "name",
                    "phone_number": "phoneNumber",
                },
                "organization_name": "organizationName",
                "tax_id": "taxId",
            },
            subscriber={
                "first_name": "firstName",
                "group_number": "groupNumber",
                "last_name": "lastName",
                "member_id": "memberId",
                "payment_responsibility_level_code": "paymentResponsibilityLevelCode",
            },
            trading_partner_name="tradingPartnerName",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            claim = await response.parse()
            assert_matches_type(ClaimSubmitResponse, claim, path=["response"])

        assert cast(Any, response.is_closed) is True
