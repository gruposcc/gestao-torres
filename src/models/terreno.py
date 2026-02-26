from decimal import Decimal
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Enum, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin

if TYPE_CHECKING:
    from .torre import Torre


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

    # TODO, ambos os pontos não podem ser o mesmo
    # TODO nao posso ter os dois repetidos em outra coluna
    lat: Mapped[float] = mapped_column(Numeric[Decimal](9, 6), nullable=False)
    lng: Mapped[float] = mapped_column(Numeric[Decimal](9, 6), nullable=False)

    # TODO
    # torres relação
    torres: Mapped[List["Torre"]] = relationship(
        "Torre", back_populates="terreno", cascade="all"
    )
    # TODO
    # despesas relaçãõ


class DespesaTerreno(BaseSQLModel):
    __tablename__ = "despesa_terreno"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


"""

 class Despesa(BaseSQLModel, TimeStampMixin):

     ## recorrente

     ## - mensal - qual dia ? - por qual periodo de tempo. / perpetua

     ## - anual - data ? - por qual periodo de tempo. / perpetua

     ## - semanal - data? - por qual periodo de tempo / -

     ## - diaria


     ## especifica

     ## ex: manutenção, compra de equipamento, etc, possivelmente relacionada futuramente com outro modelo


     ...



 class Renda(BaseSQLModel, TimeStampMixin): ...

"""
