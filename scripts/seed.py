import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.session import AsyncSessionLocal
from app.models.models import Wallet
from app.seed.constants import SEED_WALLETS


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        for item in SEED_WALLETS:
            exists = await session.execute(select(Wallet.uuid).where(Wallet.uuid == item["uuid"]))
            if exists.scalar_one_or_none() is not None:
                print(f"Wallet {item['uuid']} already exists, skip")
                continue

            await session.execute(insert(Wallet).values(uuid=item["uuid"], balance=item["balance"]))
            print(f"Created wallet {item['uuid']} balance={item['balance']}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
