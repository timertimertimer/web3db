from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import (
    EmailRelationMixin,
    TwitterRelationMixin,
    DiscordRelationMixin,
    ProxyRelationMixin,
    GithubRelationMixin
)


class Profile(
    EmailRelationMixin,
    TwitterRelationMixin,
    DiscordRelationMixin,
    ProxyRelationMixin,
    GithubRelationMixin,
    Base
):
    __tablename__ = 'profiles'
    _email_back_populates = 'profile'
    _twitter_back_populates = 'profile'
    _discord_back_populates = 'profile'
    _proxy_back_populates = 'profile'
    _github_back_populates = 'profile'
    _email_id_nullable = True

    id: Mapped[int] = mapped_column(primary_key=True)
    evm_address: Mapped[str] = mapped_column(String, unique=True)
    aptos_address: Mapped[str] = mapped_column(String, unique=True)
    solana_address: Mapped[str] = mapped_column(String, unique=True)
    evm_private: Mapped[str] = mapped_column(String)
    aptos_private: Mapped[str] = mapped_column(String)
    solana_private: Mapped[str] = mapped_column(String)
    okx_evm_address: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    okx_aptos_address: Mapped[str] = mapped_column(String, nullable=True, unique=True)
    okx_solana_address: Mapped[str] = mapped_column(String, nullable=True, unique=True)

    def __repr__(self):
        return (f'{self.id}:{self.email.login}:{self.twitter.login if self.twitter else None}:'
                f'{self.discord.login if self.discord else None}:'
                f'{self.proxy.proxy_string if self.proxy else None}')

    def __str__(self):
        return repr(self)
