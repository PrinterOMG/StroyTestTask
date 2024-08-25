from uuid import UUID
import datetime as dt

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    parent_category_id: UUID | None


class CategoryRead(CategoryBase):
    id: UUID
    created_at: dt.datetime


class ExtendedCategoryRead(CategoryRead):
    sub_categories: list['ExtendedCategoryRead'] | None


class CategoryCreate(CategoryBase): ...


class CategoryUpdate(CategoryBase): ...


class CategoryCreateResponse(BaseModel):
    id: UUID
