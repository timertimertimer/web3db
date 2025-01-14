from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .deposit import OkxDeposit


class Okx(EmailRelationMixin, Base):
    __tablename__ = 'okxs'
    _email_back_populates = 'okx'
    _email_id_nullable = False

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str]
    totp_secret: Mapped[str | None]
    api_key: Mapped[str | None]
    api_secret: Mapped[str | None]
    api_passphrase: Mapped[str | None]

    profile: Mapped['Profile'] = relationship(back_populates='okx')
    deposits: Mapped[list['OkxDeposit']] = relationship('OkxDeposit', back_populates='okx')

    def __repr__(self):
        return f'{self.id}:{self.email.login}:{self.password}'

    def __str__(self):
        return repr(self)
