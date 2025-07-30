# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["OrderRequestCreateMarketBuyParams"]


class OrderRequestCreateMarketBuyParams(TypedDict, total=False):
    payment_amount: Required[float]
    """
    Amount of currency (USD for US equities and ETFS) to pay or receive for the
    order. Must be a positive number with a precision of up to 2 decimal places.
    """

    stock_id: Required[str]
    """ID of `Stock`."""
