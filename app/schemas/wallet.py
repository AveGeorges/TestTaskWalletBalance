from decimal import Decimal

from pydantic import BaseModel, Field


class WalletResponse(BaseModel):
    balance: Decimal = Field(..., ge=0, decimal_places=2)
