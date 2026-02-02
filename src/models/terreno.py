from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Enum, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin


class Terreno(BaseSQLModel, StatusMixin, TimeStampMixin):
    __tablename__ = "terreno"

    __table_args__ = (
        CheckConstraint(
            "lat BETWEEN -90 AND 90",
            name="ck_terreno_lat_range",
        ),
        CheckConstraint(
            "lng BETWEEN -180 AND 180",
            name="ck_terreno_lng_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    lat: Mapped[float] = mapped_column(
        Numeric[Decimal](9, 6), nullable=False, unique=True
    )
    lng: Mapped[float] = mapped_column(
        Numeric[Decimal](9, 6), nullable=False, unique=True
    )

    # TODO
    # torres relação

    # TODO
    # despesas relaçãõ
