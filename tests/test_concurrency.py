import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.db.session import get_db
from app.main import app
from app.models.models import Wallet
from tests.conftest import TestSessionLocal


@pytest.mark.asyncio
async def test_parallel_withdraw_race_condition():
    """
    10 параллельных WITHDRAW по 200 при балансе 1000:
    ожидаем 5 успехов и 5 отказов, итоговый баланс 0.
    """
    wallet_id = uuid4()
    async with TestSessionLocal() as session:
        session.add(Wallet(uuid=wallet_id, balance=Decimal("1000.00")))
        await session.commit()

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    wallet_id_str = str(wallet_id)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        tasks = [
            client.post(
                f"/api/v1/wallets/{wallet_id_str}/operation",
                json={"operation_type": "WITHDRAW", "amount": "200.00"},
            )
            for _ in range(10)
        ]
        responses = await asyncio.gather(*tasks)

    app.dependency_overrides.clear()

    success = [r for r in responses if r.status_code == 200]
    failed = [r for r in responses if r.status_code == 400]

    assert len(success) == 5
    assert len(failed) == 5
    assert all(r.json()["detail"]["code"] == "insufficient_balance" for r in failed)

    async with TestSessionLocal() as session:
        result = await session.execute(select(Wallet.balance).where(Wallet.uuid == wallet_id))
        final_balance = result.scalar_one()
        assert final_balance == Decimal("0.00")
