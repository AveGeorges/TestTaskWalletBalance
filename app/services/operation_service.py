from uuid import UUID

from sqlalchemy import exists, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import api_error
from app.models.models import Operation, Wallet, _utcnow
from app.schemas.operation import OperationCreate, OperationType
from app.schemas.wallet import WalletResponse


class OperationService:
    @staticmethod
    def _apply_deposit(wallet_uuid: UUID, amount):
        return (
            update(Wallet)
            .where(Wallet.uuid == wallet_uuid)
            .values(balance=Wallet.balance + amount, updated_at=_utcnow())
            .returning(Wallet.balance)
        )

    @staticmethod
    def _apply_withdraw(wallet_uuid: UUID, amount):
        return (
            update(Wallet)
            .where(
                Wallet.uuid == wallet_uuid,
                Wallet.balance >= amount,
            )
            .values(balance=Wallet.balance - amount, updated_at=_utcnow())
            .returning(Wallet.balance)
        )

    @staticmethod
    async def create_operation(
        session: AsyncSession, wallet_uuid: UUID, operation: OperationCreate
    ):
        async with session.begin():
            if operation.operation_type == OperationType.DEPOSIT:
                statement = OperationService._apply_deposit(wallet_uuid, operation.amount)
            else:
                statement = OperationService._apply_withdraw(wallet_uuid, operation.amount)

            result = await session.execute(statement)
            new_balance = result.scalar_one_or_none()

            if new_balance is None:
                wallet_exists_result = await session.execute(
                    select(exists().where(Wallet.uuid == wallet_uuid))
                )
                wallet_exists = wallet_exists_result.scalar_one()
                if not wallet_exists:
                    raise api_error(
                        status_code=404,
                        code="wallet_not_found",
                        message="Wallet not found",
                    )
                raise api_error(
                    status_code=400,
                    code="insufficient_balance",
                    message="Insufficient balance",
                )

            await session.execute(
                insert(Operation).values(
                    wallet_id=wallet_uuid,
                    amount=operation.amount,
                    operation_type=operation.operation_type,
                    created_at=_utcnow(),
                )
            )

        return WalletResponse(balance=new_balance)
