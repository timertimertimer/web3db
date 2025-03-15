from datetime import datetime

from sqlalchemy import DateTime, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
                                                 nullable=True)


class SocialBaseModel(BaseModel):
    password_updated_at: Mapped[datetime] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)
    password: Mapped[str]


@event.listens_for(SocialBaseModel, 'before_update')
def update_password_timestamp(mapper, connection, target):
    if target.password != target.__original_password:
        target.password_updated_at = datetime.utcnow()
        target.__original_password = target.password
