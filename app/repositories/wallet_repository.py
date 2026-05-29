from decimal import Decimal
from uuid import UUID

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Wallet, _utcnow


class WalletRepository:
    @staticmethod
    async def get_by_uuid(session: AsyncSession, wallet_uuid: UUID) -> Wallet | None:
        result = await session.execute(select(Wallet).where(Wallet.uuid == wallet_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def exists(session: AsyncSession, wallet_uuid: UUID) -> bool:
        result = await session.execute(select(exists().where(Wallet.uuid == wallet_uuid)))
        return result.scalar_one()

    @staticmethod
    async def apply_deposit(
        session: AsyncSession, wallet_uuid: UUID, amount: Decimal
    ) -> Decimal | None:
        statement = (
            update(Wallet)
            .where(Wallet.uuid == wallet_uuid)
            .values(balance=Wallet.balance + amount, updated_at=_utcnow())
            .returning(Wallet.balance)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def apply_withdraw(
        session: AsyncSession, wallet_uuid: UUID, amount: Decimal
    ) -> Decimal | None:
        statement = (
            update(Wallet)
            .where(
                Wallet.uuid == wallet_uuid,
                Wallet.balance >= amount,
            )
            .values(balance=Wallet.balance - amount, updated_at=_utcnow())
            .returning(Wallet.balance)
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()
