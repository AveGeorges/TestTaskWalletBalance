from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import OperationType

__all__ = ["OperationCreate", "OperationType"]


class OperationCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    operation_type: OperationType
