from uuid import UUID


class DomainError(Exception):
    """Базовая доменная ошибка."""

    status_code: int = 400
    code: str = "domain_error"
    default_message: str = "Domain error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class WalletNotFound(DomainError):
    status_code = 404
    code = "wallet_not_found"
    default_message = "Wallet not found"

    def __init__(self, wallet_id: UUID | None = None, message: str | None = None) -> None:
        self.wallet_id = wallet_id
        super().__init__(message)


class InsufficientFunds(DomainError):
    status_code = 400
    code = "insufficient_balance"
    default_message = "Insufficient balance"

    def __init__(self, wallet_id: UUID | None = None, message: str | None = None) -> None:
        self.wallet_id = wallet_id
        super().__init__(message)
