# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OrderRequestCreateLimitSellParams"]


class OrderRequestCreateLimitSellParams(TypedDict, total=False):
    asset_quantity: Required[int]
    """Quantity of shares to trade. Must be a positive integer."""

    limit_price: Required[float]
    """Price at which to execute the order.

    Must be a positive number with a precision of up to 2 decimal places.
    """

    stock_id: Required[str]
    """ID of `Stock`."""
