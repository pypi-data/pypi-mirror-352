# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OrderRequestCreateMarketSellParams"]


class OrderRequestCreateMarketSellParams(TypedDict, total=False):
    asset_quantity: Required[float]
    """Quantity of shares to trade.

    Must be a positive number with a precision of up to 9 decimal places.
    """

    stock_id: Required[str]
    """ID of `Stock`."""
