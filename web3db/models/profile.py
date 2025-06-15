from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModel
from .mixins import (
    EmailRelationMixin,
    TwitterRelationMixin,
    DiscordRelationMixin,
    ProxyRelationMixin,
    GithubRelationMixin,
    BinanceRelationMixin,
    ByBitRelationMixin,
    OkxRelationMixin,
    MexcRelationMixin,
    BitgetRelationMixin,
)

if TYPE_CHECKING:
    from .deposit import BinanceDeposit, ByBitDeposit, OkxDeposit, MexcDeposit


class Profile(
    BaseModel,
    EmailRelationMixin,
    TwitterRelationMixin,
    DiscordRelationMixin,
    GithubRelationMixin,
    BinanceRelationMixin,
    ByBitRelationMixin,
    OkxRelationMixin,
    MexcRelationMixin,
    BitgetRelationMixin,
    ProxyRelationMixin,
    Base,
):
    __tablename__ = "profiles"
    _email_back_populates = "profile"
    _twitter_back_populates = "profile"
    _discord_back_populates = "profile"
    _proxy_back_populates = "profile"
    _github_back_populates = "profile"
    _binance_back_populates = "profile"
    _bybit_back_populates = "profile"
    _okx_back_populates = "profile"
    _mexc_back_populates = "profile"
    _email_id_nullable = True

    id: Mapped[int] = mapped_column(primary_key=True)
    evm_address: Mapped[str] = mapped_column(String, unique=True)
    aptos_address: Mapped[str] = mapped_column(String, unique=True)
    solana_address: Mapped[str] = mapped_column(String, unique=True)
    btc_native_segwit_address: Mapped[str] = mapped_column(String, unique=True)
    btc_taproot_address: Mapped[str] = mapped_column(String, unique=True)
    evm_private: Mapped[str]
    aptos_private: Mapped[str]
    solana_private: Mapped[str]
    btc_mnemo: Mapped[str]

    binance_deposit_id: Mapped[int | None] = mapped_column(
        ForeignKey("binance_deposits.id"), nullable=True, unique=True
    )
    binance_deposit: Mapped["BinanceDeposit"] = relationship(
        "BinanceDeposit", back_populates="profile"
    )

    bybit_deposit_id: Mapped[int | None] = mapped_column(
        ForeignKey("bybit_deposits.id"), nullable=True, unique=True
    )
    bybit_deposit: Mapped["ByBitDeposit"] = relationship(
        "ByBitDeposit", back_populates="profile"
    )

    okx_deposit_id: Mapped[int | None] = mapped_column(
        ForeignKey("okx_deposits.id"), nullable=True, unique=True
    )
    okx_deposit: Mapped["OkxDeposit"] = relationship(
        "OkxDeposit", back_populates="profile"
    )

    mexc_deposit_id: Mapped[int | None] = mapped_column(
        ForeignKey("mexc_deposits.id"), nullable=True, unique=True
    )
    mexc_deposit: Mapped["MexcDeposit"] = relationship(
        "MexcDeposit", back_populates="profile"
    )

    def __repr__(self):
        return (
            f"{self.id}:{self.email.login if self.email else None}:{self.twitter.login if self.twitter else None}:"
            f"{self.discord.login if self.discord else None}:{self.proxy.proxy_string if self.proxy else None}"
        )

    def __str__(self):
        return repr(self)
