# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2 import (
    ClearinghouseCheckEligibilityResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClearinghouse:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_check_eligibility(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_check_eligibility(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_check_eligibility(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        clearinghouse = client.v2.clearinghouse.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        response = client.v2.clearinghouse.with_raw_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = response.parse()
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_coordination_of_benefits(self, client: SampleHealthcare) -> None:
        with client.v2.clearinghouse.with_streaming_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = response.parse()
            assert_matches_type(object, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClearinghouse:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_check_eligibility(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.check_eligibility(
            provider_identifier="providerIdentifier",
            provider_name="providerName",
            service_type_codes=["string"],
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert_matches_type(ClearinghouseCheckEligibilityResponse, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        clearinghouse = await async_client.v2.clearinghouse.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.clearinghouse.with_raw_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clearinghouse = await response.parse()
        assert_matches_type(object, clearinghouse, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_coordination_of_benefits(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.clearinghouse.with_streaming_response.coordination_of_benefits(
            dependent_date_of_birth="dependentDateOfBirth",
            dependent_first_name="dependentFirstName",
            dependent_last_name="dependentLastName",
            encounter_date_of_service="encounterDateOfService",
            encounter_service_type_code="encounterServiceTypeCode",
            provider_name="providerName",
            provider_npi="providerNpi",
            subscriber_date_of_birth="subscriberDateOfBirth",
            subscriber_first_name="subscriberFirstName",
            subscriber_last_name="subscriberLastName",
            subscriber_member_id="subscriberMemberId",
            trading_partner_service_id="tradingPartnerServiceId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clearinghouse = await response.parse()
            assert_matches_type(object, clearinghouse, path=["response"])

        assert cast(Any, response.is_closed) is True
