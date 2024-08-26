from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from products_app.infra.database.models.base import BaseModel


class CategoryModel(BaseModel):
    __tablename__ = 'category'

    name: Mapped[str] = mapped_column()

    parent_category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey('category.id', ondelete='SET NULL'),
    )

    parent_category: Mapped[Optional['CategoryModel']] = relationship(
        back_populates='sub_categories',
        remote_side='CategoryModel.id',
    )
    sub_categories: Mapped[list['CategoryModel']] = relationship(
        back_populates='parent_category',
    )
