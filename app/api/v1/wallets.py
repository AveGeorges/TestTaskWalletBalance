from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.operation import OperationCreate
from app.schemas.wallet import WalletResponse
from app.services.operation_service import OperationService
from app.services.wallet_service import WalletService

router = APIRouter()


@router.get("/{wallet_uuid}", response_model=WalletResponse)
async def get_wallet_balance(wallet_uuid: UUID, db: AsyncSession = Depends(get_db)):
    return await WalletService.get_wallet_balance(db, wallet_uuid)


@router.post("/{wallet_uuid}/operation", response_model=WalletResponse)
async def create_operation(
    wallet_uuid: UUID, operation: OperationCreate, db: AsyncSession = Depends(get_db)
):
    return await OperationService.create_operation(db, wallet_uuid, operation)
