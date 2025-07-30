# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentRetrieveResponse"]


class DocumentRetrieveResponse(BaseModel):
    id: str

    file_name: str = FieldInfo(alias="fileName")

    mime_type: Literal["application/pdf"] = FieldInfo(alias="mimeType")

    presigned_url: str = FieldInfo(alias="presignedUrl")

    ocr_response: Optional[object] = FieldInfo(alias="ocrResponse", default=None)
