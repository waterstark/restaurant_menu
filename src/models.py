from sqlalchemy import Numeric, String, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from src.database import Base
from uuid import UUID, uuid4


class Dishes(Base):
    __tablename__ = "dish"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    submenu_id: Mapped[int] = mapped_column(
        ForeignKey("submenu.id", ondelete="CASCADE")
    )
    submenu: Mapped["SubMenu"] = relationship(
        back_populates="dish",
        cascade="all, delete",
        passive_deletes=True,
    )


class SubMenu(Base):
    __tablename__ = "submenu"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    menu_id: Mapped[UUID] = mapped_column(ForeignKey("menu.id", ondelete="CASCADE"))
    menu: Mapped["Menu"] = relationship(
        back_populates="submenu",
        passive_deletes=True,
    )
    dish: Mapped["Dishes"] = relationship(
        back_populates="submenu",
        cascade="all, delete",
    )


class Menu(Base):
    __tablename__ = "menu"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    submenu: Mapped["SubMenu"] = relationship(
        back_populates="menu",
        cascade="all, delete",
    )
