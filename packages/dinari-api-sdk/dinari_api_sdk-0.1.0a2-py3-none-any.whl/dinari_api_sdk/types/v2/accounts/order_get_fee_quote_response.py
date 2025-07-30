# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..chain import Chain
from ...._models import BaseModel

__all__ = [
    "OrderGetFeeQuoteResponse",
    "OrderFeeContractObject",
    "OrderFeeContractObjectFeeQuote",
    "OrderFeeContractObjectFee",
]


class OrderFeeContractObjectFeeQuote(BaseModel):
    deadline: int

    fee: str

    order_id: str = FieldInfo(alias="orderId")

    requester: str

    timestamp: int


class OrderFeeContractObjectFee(BaseModel):
    fee_in_eth: float
    """
    The quantity of the fee paid via payment token in
    [ETH](https://ethereum.org/en/developers/docs/intro-to-ether/#what-is-ether).
    """

    fee_in_wei: str
    """
    The quantity of the fee paid via payment token in
    [wei](https://ethereum.org/en/developers/docs/intro-to-ether/#denominations).
    """

    type: Literal["SPONSORED_NETWORK", "NETWORK", "TRADING", "ORDER", "PARTNER_ORDER", "PARTNER_TRADING"]
    """Type of fee."""


class OrderFeeContractObject(BaseModel):
    chain_id: int
    """EVM chain ID where the order is placed"""

    fee_quote: OrderFeeContractObjectFeeQuote
    """`FeeQuote` structure to pass into contracts."""

    fee_quote_signature: str
    """Signed `FeeQuote` structure to pass into contracts."""

    fees: List[OrderFeeContractObjectFee]
    """Breakdown of fees"""

    payment_token: str
    """Address of payment token used for fees"""


class OrderGetFeeQuoteResponse(BaseModel):
    chain_id: Chain
    """CAIP-2 chain ID of the blockchain where the `Order` will be placed"""

    fee: float
    """The total quantity of the fees paid via payment token."""

    order_fee_contract_object: OrderFeeContractObject
    """
    Opaque fee quote object to pass into the contract when creating an `Order`
    directly through Dinari's smart contracts.
    """
