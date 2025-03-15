from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SocialBaseModel
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .deposit import BinanceDeposit


class Binance(SocialBaseModel, EmailRelationMixin, Base):
    __tablename__ = 'binances'
    _email_back_populates = 'binance'
    _email_id_nullable = False

    id: Mapped[int] = mapped_column(primary_key=True)
    totp_secret: Mapped[str | None]
    api_key: Mapped[str | None]
    api_secret: Mapped[str | None]

    profile: Mapped['Profile'] = relationship(back_populates='binance')
    deposits: Mapped[list['BinanceDeposit']] = relationship('BinanceDeposit', back_populates='binance')

    def __repr__(self):
        return f'{self.id}:{self.email.login}:{self.password}'

    def __str__(self):
        return repr(self)
