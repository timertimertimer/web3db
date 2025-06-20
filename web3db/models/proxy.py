from typing import TYPE_CHECKING

from sqlalchemy import String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModel

if TYPE_CHECKING:
    from .profile import Profile


class Proxy(BaseModel, Base):
    __tablename__ = 'proxies'
    __table_args__ = (
        CheckConstraint("proxy_type IN ('shared', 'individual')"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    proxy_string: Mapped[str] = mapped_column(String, unique=True)
    proxy_type: Mapped[str]

    profile: Mapped['Profile'] = relationship(back_populates='proxy')

    def __repr__(self):
        return f'{self.id}:{self.proxy_string}'

    def __str__(self):
        return repr(self)
