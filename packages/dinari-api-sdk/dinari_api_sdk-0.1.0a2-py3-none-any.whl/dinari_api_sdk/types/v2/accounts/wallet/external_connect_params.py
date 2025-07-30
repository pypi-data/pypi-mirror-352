# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ...chain import Chain

__all__ = ["ExternalConnectParams"]


class ExternalConnectParams(TypedDict, total=False):
    chain_id: Required[Chain]
    """CAIP-2 formatted chain ID of the blockchain the `Wallet` to link is on."""

    nonce: Required[str]
    """Nonce contained within the connection message."""

    signature: Required[str]
    """Signature payload from signing the connection message with the `Wallet`."""

    wallet_address: Required[str]
    """Address of the `Wallet`."""
