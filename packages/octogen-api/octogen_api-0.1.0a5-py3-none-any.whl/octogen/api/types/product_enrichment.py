# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ProductEnrichment"]


class ProductEnrichment(BaseModel):
    image_with_single_product: Optional[bool] = None
    """Whether the image only contains a single product."""

    styles: Optional[List[str]] = None
    """Styles for the product."""

    tags: Optional[List[str]] = None
    """Tags for the product."""

    type: Optional[str] = None
    """Type of the product."""

    type_synonyms: Optional[List[str]] = None
    """Synonyms for the type of the product."""
