from uuid import UUID
import datetime as dt

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated, Literal


class ProductBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    name: Annotated[str, Field(min_length=3, max_length=100)]
    description: Annotated[str, Field(min_length=10, max_length=1000)]
    price: Annotated[float, Field(ge=0.01)]
    stock: Annotated[float, Field(ge=0)]
    unit: Literal['pc', 'kg', 'g', 'l', 'ml', 'm', 'cm', 'mm']
    unit_size: Annotated[float, Field(ge=0.01)]
    category_id: UUID | None
    attributes: dict


class ProductRead(ProductBase):
    id: UUID
    created_at: dt.datetime


class ProductCreate(ProductBase): ...


class ProductUpdate(ProductBase): ...


class ProductCreateResponse(BaseModel):
    id: UUID
