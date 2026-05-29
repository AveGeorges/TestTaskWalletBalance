from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import OperationType
from app.domain.exceptions import InsufficientFunds, WalletNotFound
from app.repositories.operation_repository import OperationRepository
from app.repositories.wallet_repository import WalletRepository
from app.schemas.operation import OperationCreate
from app.schemas.wallet import WalletResponse


class OperationService:
    @staticmethod
    async def create_operation(
        session: AsyncSession, wallet_uuid: UUID, operation: OperationCreate
    ):
        async with session.begin():
            if operation.operation_type == OperationType.DEPOSIT:
                new_balance = await WalletRepository.apply_deposit(
                    session, wallet_uuid, operation.amount
                )
            else:
                new_balance = await WalletRepository.apply_withdraw(
                    session, wallet_uuid, operation.amount
                )

            if new_balance is None:
                if not await WalletRepository.exists(session, wallet_uuid):
                    raise WalletNotFound(wallet_uuid)
                raise InsufficientFunds(wallet_uuid)

            await OperationRepository.create(
                session,
                wallet_id=wallet_uuid,
                amount=operation.amount,
                operation_type=operation.operation_type,
            )

        return WalletResponse(balance=new_balance)
