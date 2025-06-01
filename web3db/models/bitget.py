from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SocialBaseModel
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .deposit import BitgetDeposit


class Bitget(SocialBaseModel, EmailRelationMixin, Base):
    __tablename__ = 'bitgets'
    _email_back_populates = 'bitget'
    _email_id_nullable = False

    id: Mapped[int] = mapped_column(primary_key=True)
    totp_secret: Mapped[str | None]
    api_key: Mapped[str | None]
    api_secret: Mapped[str | None]

    profile: Mapped['Profile'] = relationship(back_populates='bitget')
    deposits: Mapped[list['BitgetDeposit']] = relationship('BitgetDeposit', back_populates='bitget')

    def __repr__(self):
        return f'{self.id}:{self.email.login}:{self.password}'

    def __str__(self):
        return repr(self)
