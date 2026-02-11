import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin


class TipoCliente(enum.Enum):
    PF = "pf"
    PJ = "pj"


class Cliente(BaseSQLModel, StatusMixin):
    __tablename__ = "cliente"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[TipoCliente] = mapped_column(
        Enum(TipoCliente, name="tipocliente", inherit_schema=True), nullable=False
    )

    __mapper_args__ = {
        "polymorphic_on": tipo,
    }


class ClientePF(Cliente, TimeStampMixin):
    __tablename__ = "cliente_pf"

    id: Mapped[int] = mapped_column(
        ForeignKey("cliente.id", ondelete="CASCADE"),
        primary_key=True,
    )

    @property
    def fullname(self):
        return f"{self.name} {self.last_name}"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": TipoCliente.PF}


class ClientePJ(Cliente, TimeStampMixin):
    __tablename__ = "clientes_pj"

    id: Mapped[int] = mapped_column(
        ForeignKey("cliente.id", ondelete="CASCADE"),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)

    __mapper_args__ = {"polymorphic_identity": TipoCliente.PJ}
