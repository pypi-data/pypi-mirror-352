# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..chain import Chain
from .order_tif import OrderTif
from .order_side import OrderSide
from .order_type import OrderType

__all__ = ["OrderGetFeeQuoteParams"]


class OrderGetFeeQuoteParams(TypedDict, total=False):
    chain_id: Required[Chain]
    """CAIP-2 chain ID of the blockchain where the `Order` will be placed."""

    contract_address: Required[str]
    """Address of the smart contract that will create the `Order`."""

    order_side: Required[OrderSide]
    """Indicates whether `Order` is a buy or sell."""

    order_tif: Required[OrderTif]
    """Time in force. Indicates how long `Order` is valid for."""

    order_type: Required[OrderType]
    """Type of `Order`."""

    stock_id: Required[str]
    """The Stock ID associated with the Order"""

    asset_token_quantity: float
    """Amount of dShare asset tokens involved.

    Required for limit `Orders` and market sell `Orders`.
    """

    limit_price: float
    """Price per asset in the asset's native currency.

    USD for US equities and ETFs. Required for limit `Orders`.
    """

    payment_token: str
    """Address of payment token."""

    payment_token_quantity: float
    """Amount of payment tokens involved. Required for market buy `Orders`."""
