import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app.db.base import Base
from app.domain.enums import OperationType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Wallet(Base):
    __tablename__ = "wallets"

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00"))
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    operations = relationship("Operation", back_populates="wallet", cascade="all, delete-orphan")


class Operation(Base):
    __tablename__ = "operations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.uuid"), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False, default=Decimal("0.00"))
    operation_type = Column(SQLAlchemyEnum(OperationType, name="operation_type"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow)

    wallet = relationship("Wallet", back_populates="operations")
