# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ....._models import BaseModel

__all__ = ["Wallet"]


class Wallet(BaseModel):
    address: str
    """Address of the `Wallet`."""

    is_aml_flagged: bool
    """Indicates whether the `Wallet` is flagged for AML violation."""

    is_managed_wallet: bool
    """Indicates whether the `Wallet` is a Dinari-managed wallet."""
