from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .discord import Discord
    from .email import Email
    from .twitter import Twitter
    from .proxy import Proxy


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
    _discord_id_nullable: bool = False
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
    _twitter_id_nullable: bool = False
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
    _proxy_id_back_populates: str = None
    _proxy_id_unique: bool = False

    @declared_attr
    def proxy_id(cls):
        return mapped_column(ForeignKey('proxies.id'), nullable=cls._proxy_id_nullable,
                             unique=cls._proxy_id_unique)

    @declared_attr
    def proxy(cls) -> Mapped['Proxy']:
        return relationship('Proxy', back_populates=cls._proxy_id_back_populates)
