from uuid import UUID


import uuid
import enum
from decimal import Decimal
from typing import TYPE_CHECKING, List

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

    # id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid[UUID](as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    terreno_id: Mapped[int] = mapped_column(ForeignKey("terreno.id"), nullable=False)
    terreno: Mapped["Terreno"] = relationship("Terreno", back_populates="torres")

    altura: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Altura em metros"
    )

    tipo: Mapped[TipoTorre] = mapped_column(
        Enum(TipoTorre), nullable=False, default=TipoTorre.OUTRO
    )

    documentos: Mapped[List[DocumentoTorre]] = relationship(
        "DocumentoTorre", back_populates="torre", cascade="all, delete-orphan"
    )

    # TODO
    # documentos


class DocumentoTorre(BaseSQLModel, StatusMixin, TimeStampMixin):
    __tablename__ = "documento_torre"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid[UUID](as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(255), nullable=False)

    path: Mapped[str] = mapped_column(String(100), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)

    torre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("torre.id"), nullable=False)
    torre: Mapped["Torre"] = relationship("Torre", back_populates="documentos")

    # Mime type (pdf, jpg, etc)
    # content_type: Mapped[str] = mapped_column(String(100), nullable=True)


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
