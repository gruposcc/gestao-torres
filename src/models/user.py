from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseSQLModel, StatusMixin, TimeStampMixin

""" from models.group import group_members

if TYPE_CHECKING:
    from models.group import Group
 """


class User(BaseSQLModel, StatusMixin, TimeStampMixin):
    __tablename__ = "user"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    # username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), index=True, unique=True)

    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)

    password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # set nullable para true

    # from_ad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    """ groups: Mapped[list["Group"]] = relationship(
        "Group", secondary=group_members, back_populates="members", lazy="selectin"
    )
    """
