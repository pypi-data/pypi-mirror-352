# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = [
    "ClaimSubmitParams",
    "ClaimInformation",
    "ClaimInformationClaimCodeInformation",
    "ClaimInformationClaimDateInformation",
    "ClaimInformationPrincipalDiagnosis",
    "ClaimInformationServiceLine",
    "ClaimInformationServiceLineInstitutionalService",
    "Provider",
    "ProviderContactInformation",
    "ProviderAddress",
    "Receiver",
    "Submitter",
    "SubmitterContactInformation",
    "Subscriber",
]


class ClaimSubmitParams(TypedDict, total=False):
    claim_information: Required[Annotated[ClaimInformation, PropertyInfo(alias="claimInformation")]]

    idempotency_key: Required[Annotated[str, PropertyInfo(alias="idempotencyKey")]]

    is_testing: Required[Annotated[bool, PropertyInfo(alias="isTesting")]]

    providers: Required[Iterable[Provider]]

    receiver: Required[Receiver]

    submitter: Required[Submitter]

    subscriber: Required[Subscriber]

    trading_partner_name: Required[Annotated[str, PropertyInfo(alias="tradingPartnerName")]]

    trading_partner_service_id: Required[Annotated[str, PropertyInfo(alias="tradingPartnerServiceId")]]


class ClaimInformationClaimCodeInformation(TypedDict, total=False):
    admission_source_code: Required[Annotated[str, PropertyInfo(alias="admissionSourceCode")]]

    admission_type_code: Required[Annotated[str, PropertyInfo(alias="admissionTypeCode")]]

    patient_status_code: Required[Annotated[str, PropertyInfo(alias="patientStatusCode")]]


class ClaimInformationClaimDateInformation(TypedDict, total=False):
    admission_date_and_hour: Required[Annotated[str, PropertyInfo(alias="admissionDateAndHour")]]

    statement_begin_date: Required[Annotated[str, PropertyInfo(alias="statementBeginDate")]]

    statement_end_date: Required[Annotated[str, PropertyInfo(alias="statementEndDate")]]


class ClaimInformationPrincipalDiagnosis(TypedDict, total=False):
    principal_diagnosis_code: Required[Annotated[str, PropertyInfo(alias="principalDiagnosisCode")]]

    qualifier_code: Annotated[str, PropertyInfo(alias="qualifierCode")]


class ClaimInformationServiceLineInstitutionalService(TypedDict, total=False):
    line_item_charge_amount: Required[Annotated[str, PropertyInfo(alias="lineItemChargeAmount")]]

    procedure_code: Required[Annotated[str, PropertyInfo(alias="procedureCode")]]

    service_line_revenue_code: Required[Annotated[str, PropertyInfo(alias="serviceLineRevenueCode")]]

    measurement_unit: Annotated[str, PropertyInfo(alias="measurementUnit")]

    procedure_identifier: Annotated[str, PropertyInfo(alias="procedureIdentifier")]

    service_unit_count: Annotated[str, PropertyInfo(alias="serviceUnitCount")]


class ClaimInformationServiceLine(TypedDict, total=False):
    institutional_service: Required[
        Annotated[ClaimInformationServiceLineInstitutionalService, PropertyInfo(alias="institutionalService")]
    ]

    service_date: Required[Annotated[str, PropertyInfo(alias="serviceDate")]]

    service_date_end: Annotated[str, PropertyInfo(alias="serviceDateEnd")]


class ClaimInformation(TypedDict, total=False):
    benefits_assignment_certification_indicator: Required[
        Annotated[str, PropertyInfo(alias="benefitsAssignmentCertificationIndicator")]
    ]

    claim_charge_amount: Required[Annotated[str, PropertyInfo(alias="claimChargeAmount")]]

    claim_code_information: Required[
        Annotated[ClaimInformationClaimCodeInformation, PropertyInfo(alias="claimCodeInformation")]
    ]

    claim_date_information: Required[
        Annotated[ClaimInformationClaimDateInformation, PropertyInfo(alias="claimDateInformation")]
    ]

    claim_filing_code: Required[Annotated[str, PropertyInfo(alias="claimFilingCode")]]

    claim_frequency_code: Required[Annotated[str, PropertyInfo(alias="claimFrequencyCode")]]

    place_of_service_code: Required[Annotated[str, PropertyInfo(alias="placeOfServiceCode")]]

    plan_participation_code: Required[Annotated[str, PropertyInfo(alias="planParticipationCode")]]

    principal_diagnosis: Required[
        Annotated[ClaimInformationPrincipalDiagnosis, PropertyInfo(alias="principalDiagnosis")]
    ]

    release_information_code: Required[Annotated[str, PropertyInfo(alias="releaseInformationCode")]]

    service_lines: Required[Annotated[Iterable[ClaimInformationServiceLine], PropertyInfo(alias="serviceLines")]]


class ProviderContactInformation(TypedDict, total=False):
    name: Required[str]

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]


class ProviderAddress(TypedDict, total=False):
    address1: Required[str]

    city: Required[str]

    postal_code: Required[Annotated[str, PropertyInfo(alias="postalCode")]]

    state: Required[str]


class Provider(TypedDict, total=False):
    contact_information: Required[Annotated[ProviderContactInformation, PropertyInfo(alias="contactInformation")]]

    npi: Required[str]

    provider_type: Required[Annotated[str, PropertyInfo(alias="providerType")]]

    address: ProviderAddress

    employer_id: Annotated[str, PropertyInfo(alias="employerId")]

    first_name: Annotated[str, PropertyInfo(alias="firstName")]

    last_name: Annotated[str, PropertyInfo(alias="lastName")]

    organization_name: Annotated[str, PropertyInfo(alias="organizationName")]


class Receiver(TypedDict, total=False):
    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]


class SubmitterContactInformation(TypedDict, total=False):
    name: Required[str]

    phone_number: Required[Annotated[str, PropertyInfo(alias="phoneNumber")]]


class Submitter(TypedDict, total=False):
    contact_information: Required[Annotated[SubmitterContactInformation, PropertyInfo(alias="contactInformation")]]

    organization_name: Required[Annotated[str, PropertyInfo(alias="organizationName")]]

    tax_id: Required[Annotated[str, PropertyInfo(alias="taxId")]]


class Subscriber(TypedDict, total=False):
    first_name: Required[Annotated[str, PropertyInfo(alias="firstName")]]

    group_number: Required[Annotated[str, PropertyInfo(alias="groupNumber")]]

    last_name: Required[Annotated[str, PropertyInfo(alias="lastName")]]

    member_id: Required[Annotated[str, PropertyInfo(alias="memberId")]]

    payment_responsibility_level_code: Required[Annotated[str, PropertyInfo(alias="paymentResponsibilityLevelCode")]]
