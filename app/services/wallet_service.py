from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import WalletNotFound
from app.repositories.wallet_repository import WalletRepository
from app.schemas.wallet import WalletResponse


class WalletService:
    @staticmethod
    async def get_wallet_balance(session: AsyncSession, wallet_uuid: UUID):
        wallet = await WalletRepository.get_by_uuid(session, wallet_uuid)

        if wallet is None:
            raise WalletNotFound(wallet_uuid)

        return WalletResponse(balance=wallet.balance)
