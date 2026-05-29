from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import api_error
from app.models.models import Wallet
from app.schemas.wallet import WalletResponse


class WalletService:
    @staticmethod
    async def get_wallet_balance(session: AsyncSession, wallet_uuid: UUID):
        query = select(Wallet).where(Wallet.uuid == wallet_uuid)
        result = await session.execute(query)
        wallet = result.scalar_one_or_none()

        if wallet is None:
            raise api_error(
                status_code=404,
                code="wallet_not_found",
                message="Wallet not found",
            )

        return WalletResponse(balance=wallet.balance)
