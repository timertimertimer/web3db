from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SocialBaseModel
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .deposit import MexcDeposit


class Mexc(SocialBaseModel, EmailRelationMixin, Base):
    __tablename__ = 'mexcs'
    _email_back_populates = 'mexc'
    _email_id_nullable = False

    id: Mapped[int] = mapped_column(primary_key=True)
    totp_secret: Mapped[str | None]
    api_key: Mapped[str | None]
    api_secret: Mapped[str | None]

    profile: Mapped['Profile'] = relationship(back_populates='mexc')
    deposits: Mapped[list['MexcDeposit']] = relationship('MexcDeposit', back_populates='mexc')

    def __repr__(self):
        return f'{self.id}:{self.email.login}:{self.password}'

    def __str__(self):
        return repr(self)
