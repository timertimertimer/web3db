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

    id: Mapped[int] = mapped_column(primary_key=True)
    evm_address: Mapped[str] = mapped_column(String)
    aptos_address: Mapped[str] = mapped_column(String)
    solana_address: Mapped[str] = mapped_column(String)
    evm_private: Mapped[str] = mapped_column(String)
    aptos_private: Mapped[str] = mapped_column(String)
    solana_private: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return (f'{self.id}:{self.email.login}:{self.twitter.login}:{self.discord.login}:'
                f'{self.proxy.proxy_string if self.proxy else None}')

    def __str__(self):
        return repr(self)
