from uuid import UUID
import enum
from datetime import datetime
from models.base import BaseSQLModel, TimeStampMixin
import uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Uuid, String, Enum, DateTime, Numeric, Integer, ForeignKey
from decimal import Decimal
from typing import TYPE_CHECKING, List

from models.clientes import Cliente

if TYPE_CHECKING:
    from models.torre import Torre


class RecorrenciaContrato(enum.Enum):
    MENSAL = "Mensal"
    ANUAL = "Anual"
    UNICA = "Única"


class FaceDirecao(enum.Enum):
    NORTE = "Norte"
    SUL = "Sul"
    LESTE = "Leste"
    OESTE = "Oeste"


class Altura(BaseSQLModel, TimeStampMixin):
    __tablename__ = "altura"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid[UUID](as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    metro_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    metro_final: Mapped[int] = mapped_column(Integer, nullable=False)
    face: Mapped[FaceDirecao] = mapped_column(Enum(FaceDirecao), nullable=False)

    contrato_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("contrato.id"), nullable=False
    )

    contrato: Mapped["Contrato"] = relationship(
        "Contrato", back_populates="alturas", lazy="selectin"
    )


class Contrato(BaseSQLModel, TimeStampMixin):
    __tablename__ = "contrato"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid[UUID](as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    valor: Mapped[Decimal] = mapped_column(Numeric[Decimal](10, 2), nullable=False)

    data_inicial: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=False
    )
    data_final: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=True
    )

    recorrencia: Mapped[RecorrenciaContrato] = mapped_column(
        Enum(RecorrenciaContrato), nullable=False, default=RecorrenciaContrato.MENSAL
    )

    # relações
    alturas: Mapped[List["Altura"]] = relationship(
        "Altura",
        back_populates="contrato",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    torre: Mapped["Torre"] = relationship(
        "Torre", back_populates="contratos", lazy="selectin"
    )
    torre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("torre.id"), nullable=False)

    cliente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cliente.id"), nullable=False
    )
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="contratos")

    # TODO
    # created_by
    # mixin ownable
