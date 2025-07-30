# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerPatientAdjustmentParams"]


class LedgerPatientAdjustmentParams(TypedDict, total=False):
    amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="amountUsdCents")]]
    """Adjustment amount in cents (positive or negative)."""

    ik: Required[str]
    """Idempotency key for the adjustment."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Order ID associated with the adjustment."""

    patient_id: Required[Annotated[str, PropertyInfo(alias="patientId")]]
    """Identifier of the patient for the adjustment."""

    reason: Required[str]
    """Reason for the adjustment."""
