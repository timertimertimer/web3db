from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, SocialBaseModel
from .mixins import EmailRelationMixin

if TYPE_CHECKING:
    from .profile import Profile


class Github(SocialBaseModel, EmailRelationMixin, Base):
    __tablename__ = 'githubs'
    _email_id_nullable = False
    _email_back_populates = 'github'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True)

    profile: Mapped['Profile'] = relationship(back_populates='github')

    def __repr__(self):
        return f'{self.id}:{self.login}:{self.password}'

    def __str__(self):
        return repr(self)
