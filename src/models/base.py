import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseSQLModel(DeclarativeBase):
    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        )
        return f"<{self.__class__.__name__}({attrs})>"


class ObjectStatus(enum.Enum):
    ENABLE = "enable"
    DISABLE = "disable"
    DELETED = "deleted"


class StatusMixin:
    status: Mapped[ObjectStatus] = mapped_column(
        Enum(ObjectStatus), default=ObjectStatus.ENABLE, nullable=False
    )


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
