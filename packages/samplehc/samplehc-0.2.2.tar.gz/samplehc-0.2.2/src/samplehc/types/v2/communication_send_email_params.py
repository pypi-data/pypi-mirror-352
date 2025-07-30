# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CommunicationSendEmailParams", "Attachment"]


class CommunicationSendEmailParams(TypedDict, total=False):
    body: Required[str]
    """The main content/body of the email"""

    subject: Required[str]
    """The subject line of the email"""

    to: Required[str]
    """The email address of the recipient"""

    attachments: Iterable[Attachment]
    """Optional array of file attachment IDs to include with the email"""

    enable_encryption: Annotated[bool, PropertyInfo(alias="enableEncryption")]
    """Whether to encrypt the email content and send a secure link instead"""

    zip_attachments: Annotated[bool, PropertyInfo(alias="zipAttachments")]
    """Whether to compress all attachments into a single zip file before sending"""


class Attachment(TypedDict, total=False):
    id: Required[str]
