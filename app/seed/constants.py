from decimal import Decimal
from uuid import UUID

WALLET_UUID_MAIN = UUID("11111111-1111-1111-1111-111111111111")
WALLET_UUID_SECONDARY = UUID("22222222-2222-2222-2222-222222222222")

SEED_WALLETS = [
    {"uuid": WALLET_UUID_MAIN, "balance": Decimal("1000.00")},
    {"uuid": WALLET_UUID_SECONDARY, "balance": Decimal("500.00")},
]
