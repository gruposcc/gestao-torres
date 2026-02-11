import enum
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin

if TYPE_CHECKING:
    from .terreno import Terreno


class TipoTorre(enum.Enum):
    ESTAIADA = "Estaiada"
    AUTO_LINEAR = "Autoportante linear"
    AUTO_MISTA = "Autoportante mista"
    AUTO_TRIAN = "Autoportante triangular"
    OUTRO = "Outro"


class Torre(BaseSQLModel, StatusMixin, TimeStampMixin):
    __tablename__ = "torre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    terreno_id: Mapped[int] = mapped_column(ForeignKey("terreno.id"), nullable=False)
    terreno: Mapped["Terreno"] = relationship("Terreno", back_populates="torres")

    # TODO
    altura: Mapped[Decimal] = mapped_column(
        Numeric[Decimal](6, 2), nullable=False, comment="Altura em metros"
    )

    tipo: Mapped[TipoTorre] = mapped_column(
        Enum(TipoTorre), nullable=False, default=TipoTorre.OUTRO
    )

    # TODO
    # tipo


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
