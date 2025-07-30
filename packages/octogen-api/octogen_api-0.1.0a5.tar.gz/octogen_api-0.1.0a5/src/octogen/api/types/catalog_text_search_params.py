# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CatalogTextSearchParams", "Facet"]


class CatalogTextSearchParams(TypedDict, total=False):
    text: Required[str]
    """
    The text is converted to a vector embedding and used to search for products in
    the e-commerce catalog with pre-computed product embeddings.
    """

    facets: Optional[Iterable[Facet]]
    """The search results will be filtered by the specified facets."""

    limit: int
    """The maximum number of results to return from the search. The default is 10."""

    price_max: Optional[float]
    """
    The products will be filtered to have a price less than or equal to the
    specified value.
    """

    price_min: Optional[float]
    """
    The products will be filtered to have a price greater than or equal to the
    specified value.
    """


class Facet(TypedDict, total=False):
    name: Required[Literal["brand_name", "product_type"]]

    values: Required[List[str]]
    """List of values to filter by.

    They should all be lowercase. Facet values can be phrases, so make sure to
    include the spaces.
    """
