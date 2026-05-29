from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_wallet_balance(client: AsyncClient, wallet_uuid: str):
    response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 200
    assert response.json() == {"balance": "1000.00"}


@pytest.mark.asyncio
async def test_get_wallet_not_found(client: AsyncClient):
    unknown_uuid = str(uuid4())
    response = await client.get(f"/api/v1/wallets/{unknown_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "wallet_not_found"


@pytest.mark.asyncio
async def test_deposit(client: AsyncClient, wallet_uuid: str):
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "250.50"},
    )
    assert response.status_code == 200
    assert response.json() == {"balance": "1250.50"}


@pytest.mark.asyncio
async def test_withdraw(client: AsyncClient, wallet_uuid: str):
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "400.00"},
    )
    assert response.status_code == 200
    assert response.json() == {"balance": "600.00"}


@pytest.mark.asyncio
async def test_withdraw_insufficient_balance(client: AsyncClient, wallet_uuid: str):
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "5000.00"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "insufficient_balance"


@pytest.mark.asyncio
async def test_operation_wallet_not_found(client: AsyncClient):
    unknown_uuid = str(uuid4())
    response = await client.post(
        f"/api/v1/wallets/{unknown_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "10.00"},
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "wallet_not_found"


@pytest.mark.asyncio
async def test_invalid_operation_type(client: AsyncClient, wallet_uuid: str):
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "TRANSFER", "amount": "10.00"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_amount(client: AsyncClient, wallet_uuid: str):
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "-1"},
    )
    assert response.status_code == 422
