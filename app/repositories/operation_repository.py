from decimal import Decimal
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import OperationType
from app.models.models import Operation, _utcnow


class OperationRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        wallet_id: UUID,
        amount: Decimal,
        operation_type: OperationType,
    ) -> None:
        await session.execute(
            insert(Operation).values(
                wallet_id=wallet_id,
                amount=amount,
                operation_type=operation_type,
                created_at=_utcnow(),
            )
        )
