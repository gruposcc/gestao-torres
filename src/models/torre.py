from uuid import UUID


import uuid
import enum
from decimal import Decimal
from typing import TYPE_CHECKING, List
import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Uuid,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin

if TYPE_CHECKING:
    from .terreno import Terreno
    from .contratos import Contrato


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

    despesas: Mapped[List[DespesaTorre]] = relationship(
        "DespesaTorre", back_populates="torre", cascade="all, delete-orphan"
    )

    contratos: Mapped[List[Contrato]] = relationship(
        "Contrato", back_populates="torre", cascade="all, delete-orphan"
    )


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


class RecorrenciaDespesa(enum.Enum):
    UNICA = "Única"
    DIARIA = "Diaria"
    MENSAL = "Mensal"
    ANUAL = "Anual"


class DespesaTorre(BaseSQLModel, TimeStampMixin):
    __tablename__ = "despesa_torre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    torre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("torre.id"), nullable=False)
    torre: Mapped["Torre"] = relationship(
        "Torre", back_populates="despesas", lazy="selectin"
    )

    valor: Mapped[Decimal] = mapped_column(Numeric[Decimal](10, 2), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric[Decimal], nullable=True)

    recorrencia: Mapped[RecorrenciaDespesa] = mapped_column(
        Enum(RecorrenciaDespesa), nullable=False, default=RecorrenciaDespesa.UNICA
    )
    # DATE RANGE

    perpetua: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    data_inicio: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=False
    )

    data_final: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    description: Mapped[str] = mapped_column(String(255), nullable=True)
