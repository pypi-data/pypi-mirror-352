# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerNewOrderParams"]


class LedgerNewOrderParams(TypedDict, total=False):
    claim_amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="claimAmountUsdCents")]]
    """Total amount of the claim, in cents."""

    institution_amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="institutionAmountUsdCents")]]
    """Amount allocated to or from the institution, in cents."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Unique identifier for the order being processed."""

    patient_amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="patientAmountUsdCents")]]
    """Amount allocated to or from the patient, in cents."""

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]
    """Identifier of the patient related to this ledger entry."""

    unallocated_amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="unallocatedAmountUsdCents")]]
    """Any portion of the order amount that remains unallocated, in cents."""

    claim_id: Annotated[str, PropertyInfo(alias="claimId")]
    """Identifier of the claim associated with this ledger entry."""

    institution_id: Annotated[str, PropertyInfo(alias="institutionId")]
    """Identifier of the financial institution involved."""

    insurance_id: Annotated[str, PropertyInfo(alias="insuranceId")]
    """Identifier of the insurance provider. Payments are often grouped by this ID."""
