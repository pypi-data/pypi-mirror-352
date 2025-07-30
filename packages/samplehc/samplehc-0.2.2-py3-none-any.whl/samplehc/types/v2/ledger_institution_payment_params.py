# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["LedgerInstitutionPaymentParams"]


class LedgerInstitutionPaymentParams(TypedDict, total=False):
    amount_usd_cents: Required[Annotated[float, PropertyInfo(alias="amountUsdCents")]]
    """Payment amount in cents."""

    claim_id: Required[Annotated[str, PropertyInfo(alias="claimId")]]
    """Identifier of the claim associated with this payment."""

    ik: Required[str]
    """Idempotency key for the payment."""

    institution_id: Required[Annotated[str, PropertyInfo(alias="institutionId")]]
    """Identifier of the institution for the payment."""

    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]
    """Order ID associated with the payment."""
