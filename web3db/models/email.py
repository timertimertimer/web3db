from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .discord import Discord
    from .profile import Profile
    from .twitter import Twitter
    from .github import Github
    from .bybit import ByBit
    from .mexc import Mexc
    from .okx import Okx
    from .binance import Binance


class Email(Base):
    __tablename__ = 'emails'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str]
    totp_secret: Mapped[str | None]
    refresh_token: Mapped[str | None]
    client_id: Mapped[str | None]

    discord: Mapped['Discord'] = relationship(back_populates='email')
    twitter: Mapped['Twitter'] = relationship(back_populates='email')
    profile: Mapped['Profile'] = relationship(back_populates='email')
    github: Mapped['Github'] = relationship(back_populates='email')
    bybit: Mapped['ByBit'] = relationship(back_populates='email')
    mexc: Mapped['Mexc'] = relationship(back_populates='email')
    binance: Mapped['Binance'] = relationship(back_populates='email')
    okx: Mapped['Okx'] = relationship(back_populates='email')

    def __repr__(self):
        return f'{self.id}:{self.login}:{self.password}'

    def __str__(self):
        return repr(self)
