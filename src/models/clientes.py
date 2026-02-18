import enum
import uuid
from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin
from typing import TYPE_CHECKING, List


if TYPE_CHECKING:
    from .contratos import Contrato


class TipoCliente(enum.Enum):
    PF = "pf"
    PJ = "pj"


class Cliente(BaseSQLModel, StatusMixin):
    __tablename__ = "cliente"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tipo: Mapped[TipoCliente] = mapped_column(
        Enum(TipoCliente, name="tipocliente"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    contratos: Mapped[List["Contrato"]] = relationship(
        "Contrato", back_populates="cliente", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": tipo,
    }


class ClientePF(Cliente, TimeStampMixin):
    __tablename__ = "cliente_pf"

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cliente.id", ondelete="CASCADE"),
        primary_key=True,
    )

    @property
    def fullname(self):
        return f"{self.name} {self.last_name}"

    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": TipoCliente.PF}


class ClientePJ(Cliente, TimeStampMixin):
    __tablename__ = "cliente_pj"

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cliente.id", ondelete="CASCADE"),
        primary_key=True,
    )

    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": TipoCliente.PJ}
