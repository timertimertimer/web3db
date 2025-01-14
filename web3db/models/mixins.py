from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .discord import Discord
    from .email import Email
    from .twitter import Twitter
    from .proxy import Proxy
    from .github import Github
    from .binance import Binance
    from .bybit import ByBit
    from .okx import Okx
    from .mexc import Mexc
    from .deposit import BinanceDeposit, ByBitDeposit, OkxDeposit, MexcDeposit


class EmailRelationMixin:
    _email_id_nullable: bool = False
    _email_back_populates: str = None
    _email_id_unique: bool = True

    @declared_attr
    def email_id(cls):
        return mapped_column(ForeignKey('emails.id'), nullable=cls._email_id_nullable, unique=cls._email_id_unique)

    @declared_attr
    def email(cls) -> Mapped['Email']:
        return relationship('Email', back_populates=cls._email_back_populates)


class DiscordRelationMixin:
    _discord_id_nullable: bool = True
    _discord_back_populates: str = None
    _discord_id_unique: bool = True

    @declared_attr
    def discord_id(cls):
        return mapped_column(ForeignKey('discords.id'), nullable=cls._discord_id_nullable,
                             unique=cls._discord_id_unique)

    @declared_attr
    def discord(cls) -> Mapped['Discord']:
        return relationship('Discord', back_populates=cls._discord_back_populates)


class TwitterRelationMixin:
    _twitter_id_nullable: bool = True
    _twitter_back_populates: str = None
    _twitter_id_unique: bool = True

    @declared_attr
    def twitter_id(cls):
        return mapped_column(ForeignKey('twitters.id'), nullable=cls._twitter_id_nullable,
                             unique=cls._twitter_id_unique)

    @declared_attr
    def twitter(cls) -> Mapped['Twitter']:
        return relationship('Twitter', back_populates=cls._twitter_back_populates)


class ProxyRelationMixin:
    _proxy_id_nullable: bool = False
    _proxy_back_populates: str = None
    _proxy_id_unique: bool = False

    @declared_attr
    def proxy_id(cls):
        return mapped_column(ForeignKey('proxies.id'), nullable=cls._proxy_id_nullable, unique=cls._proxy_id_unique)

    @declared_attr
    def proxy(cls) -> Mapped['Proxy']:
        return relationship('Proxy', back_populates=cls._proxy_back_populates)


class GithubRelationMixin:
    _github_id_nullable: bool = True
    _github_back_populates: str = None
    _github_id_unique: bool = True

    @declared_attr
    def github_id(cls):
        return mapped_column(ForeignKey('githubs.id'), nullable=cls._github_id_nullable, unique=cls._github_id_unique)

    @declared_attr
    def github(cls) -> Mapped['Github']:
        return relationship('Github', back_populates=cls._github_back_populates)


class BinanceRelationMixin:
    _binance_id_nullable: bool = True
    _binance_back_populates: str = None
    _binance_id_unique: bool = True

    @declared_attr
    def binance_id(cls):
        return mapped_column(ForeignKey('binances.id'), nullable=cls._binance_id_nullable,
                             unique=cls._binance_id_unique)

    @declared_attr
    def binance(cls) -> Mapped['Binance']:
        return relationship('Binance', back_populates=cls._binance_back_populates)


class ByBitRelationMixin:
    _bybit_id_nullable: bool = True
    _bybit_back_populates: str = None
    _bybit_id_unique: bool = True

    @declared_attr
    def bybit_id(cls):
        return mapped_column(ForeignKey('bybits.id'), nullable=cls._bybit_id_nullable, unique=cls._bybit_id_unique)

    @declared_attr
    def bybit(cls) -> Mapped['ByBit']:
        return relationship('ByBit', back_populates=cls._bybit_back_populates)


class OkxRelationMixin:
    _okx_id_nullable: bool = True
    _okx_back_populates: str = None
    _okx_id_unique: bool = True

    @declared_attr
    def okx_id(cls):
        return mapped_column(ForeignKey('okxs.id'), nullable=cls._okx_id_nullable, unique=cls._okx_id_unique)

    @declared_attr
    def okx(cls) -> Mapped['Okx']:
        return relationship('Okx', back_populates=cls._okx_back_populates)


class MexcRelationMixin:
    _mexc_id_nullable: bool = True
    _mexc_back_populates: str = None
    _mexc_id_unique: bool = True

    @declared_attr
    def mexc_id(cls):
        return mapped_column(ForeignKey('mexcs.id'), nullable=cls._mexc_id_nullable, unique=cls._mexc_id_unique)

    @declared_attr
    def mexc(cls) -> Mapped['Mexc']:
        return relationship('Mexc', back_populates=cls._mexc_back_populates)
