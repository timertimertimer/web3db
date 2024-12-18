from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .discord import Discord
    from .profile import RemoteProfile
    from .twitter import Twitter
    from .github import Github
    from .bybit import ByBit
    from .mexc import Mexc


class Email(Base):
    __tablename__ = 'emails'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    totp_secret: Mapped[str] = mapped_column(String, nullable=True)

    discord: Mapped['Discord'] = relationship(back_populates='email')
    twitter: Mapped['Twitter'] = relationship(back_populates='email')
    profile: Mapped['RemoteProfile'] = relationship(back_populates='email')
    github: Mapped['Github'] = relationship(back_populates='email')
    bybit: Mapped['ByBit'] = relationship(back_populates='email')
    mexc: Mapped['Mexc'] = relationship(back_populates='email')

    def __repr__(self):
        return f'{self.id}:{self.login}:{self.password}'

    def __str__(self):
        return repr(self)
