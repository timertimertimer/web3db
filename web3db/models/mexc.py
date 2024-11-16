from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import EmailRelationMixin


class Mexc(EmailRelationMixin, Base):
    __tablename__ = 'mexcs'
    _email_back_populates = 'mexc'
    _email_id_nullable = False

    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(String)
    totp_secret: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f'{self.id}:{self.email.login}:{self.password}'

    def __str__(self):
        return repr(self)
