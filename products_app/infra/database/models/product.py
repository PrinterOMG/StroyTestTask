from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from products_app.infra.database.models.base import BaseModel


if TYPE_CHECKING:
    from products_app.infra.database.models.category import CategoryModel


class ProductModel(BaseModel):
    __tablename__ = 'product'

    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(Numeric(precision=12, scale=2))
    stock: Mapped[float] = mapped_column(Numeric(precision=12, scale=2))
    unit: Mapped[str] = mapped_column()
    unit_size: Mapped[float] = mapped_column(Numeric(precision=12, scale=2))
    attributes: Mapped[dict] = mapped_column(JSONB)

    category_id: Mapped[UUID] = mapped_column(ForeignKey('category.id'))

    category: Mapped['CategoryModel'] = relationship()
