# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ExternalGetNonceParams"]


class ExternalGetNonceParams(TypedDict, total=False):
    wallet_address: Required[str]
    """Address of the `Wallet` to connect."""
