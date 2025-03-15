from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModel
from .mixins import (
    BinanceRelationMixin,
    ByBitRelationMixin,
    OkxRelationMixin,
    MexcRelationMixin
)

if TYPE_CHECKING:
    from .profile import Profile


class Deposit:
    id: Mapped[int] = mapped_column(primary_key=True)
    evm: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    aptos: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    solana: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "evm IS NOT NULL OR aptos IS NOT NULL OR solana IS NOT NULL",
            name="check_at_least_one_not_null"
        ),
    )


class BinanceDeposit(BaseModel, Deposit, BinanceRelationMixin, Base):
    __tablename__ = 'binance_deposits'
    _binance_back_populates = 'deposits'
    _binance_id_nullable = False
    _binance_id_unique = False

    profile: Mapped['Profile'] = relationship(back_populates='binance_deposit')


class ByBitDeposit(BaseModel, Deposit, ByBitRelationMixin, Base):
    __tablename__ = 'bybit_deposits'
    _bybit_back_populates = 'deposits'
    _bybit_id_nullable = False
    _bybit_id_unique = False

    profile: Mapped['Profile'] = relationship(back_populates='bybit_deposit')


class OkxDeposit(BaseModel, Deposit, OkxRelationMixin, Base):
    __tablename__ = 'okx_deposits'
    _okx_back_populates = 'deposits'
    _okx_id_nullable = False
    _okx_id_unique = False

    profile: Mapped['Profile'] = relationship(back_populates='okx_deposit')


class MexcDeposit(BaseModel, Deposit, MexcRelationMixin, Base):
    __tablename__ = 'mexc_deposits'
    _mexc_back_populates = 'deposits'
    _mexc_id_nullable = False
    _mexc_id_unique = False

    profile: Mapped['Profile'] = relationship(back_populates='mexc_deposit')
