from uuid import UUID
import enum
from datetime import datetime
from models.base import BaseSQLModel, TimeStampMixin
import uuid
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Uuid, String, Enum, DateTime, Numeric, Integer, ForeignKey
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.torre import Torre
    from models.clientes import Cliente


class RecorrenciaContrato(enum.Enum):
    MENSAL = "Mensal"
    ANUAL = "Anual"


class FaceDirecao(enum.Enum):
    NORTE = "Norte"
    SUL = "Sul"
    LESTE = "Leste"
    OESTE = "Oeste"


class Contrato(BaseSQLModel, TimeStampMixin):
    __tablename__ = "contrato"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid[UUID](as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # SOMENTE METRO CHEIO
    metro_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    metro_final: Mapped[int] = mapped_column(Integer, nullable=False)

    # DECIMAL?
    valor: Mapped[Decimal] = mapped_column(Numeric[Decimal](10, 2), nullable=False)

    data_inicial: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=False
    )
    data_final: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=None, nullable=False
    )

    recorrencia: Mapped[RecorrenciaContrato] = mapped_column(
        Enum(RecorrenciaContrato), nullable=False, default=RecorrenciaContrato.MENSAL
    )

    face: Mapped[FaceDirecao] = mapped_column(Enum(FaceDirecao), nullable=False)

    # relações
    torre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("torre.id"), nullable=False)
    torre: Mapped["Torre"] = relationship(
        "Torre", back_populates="contratos", lazy="selectin"
    )

    cliente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cliente.id"), nullable=False
    )
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="contratos")
