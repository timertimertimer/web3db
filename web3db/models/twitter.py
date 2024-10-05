from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import RemoteProfile


class Twitter(EmailRelationMixin, Base):
    __tablename__ = 'twitters'
    _email_id_nullable = True
    _email_back_populates = 'twitter'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    auth_token: Mapped[str] = mapped_column(String, unique=True)
    ready: Mapped[bool] = mapped_column(Boolean, default=False)
    totp_secret: Mapped[str] = mapped_column(String, nullable=True)
    backup_code: Mapped[str] = mapped_column(String, nullable=True)

    profile: Mapped['RemoteProfile'] = relationship(back_populates='twitter')

    def __repr__(self):
        return f'{self.id}:{self.login}:{self.password}:{self.auth_token}'

    def __str__(self):
        return repr(self)
