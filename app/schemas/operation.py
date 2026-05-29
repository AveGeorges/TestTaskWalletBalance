from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class OperationCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    operation_type: OperationType
