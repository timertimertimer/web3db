from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import RemoteProfile


class Discord(EmailRelationMixin, Base):
    __tablename__ = 'discords'
    _email_id_nullable = False
    _email_back_populates = 'discord'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    auth_token: Mapped[str] = mapped_column(String, unique=True)

    profile: Mapped['RemoteProfile'] = relationship(back_populates='discord')

    def __repr__(self):
        return f'{self.id}:{self.login}:{self.password}:{self.auth_token}'

    def __str__(self):
        return repr(self)
