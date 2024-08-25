from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class NewProductDTO:
    name: str
    description: str
    price: Decimal
    stock: Decimal
    unit: str
    unit_size: Decimal
    category_id: str
    attributes: dict


@dataclass(slots=True)
class UpdateProductDTO:
    id: str
    name: str
    description: str
    price: Decimal
    stock: Decimal
    unit: str
    unit_size: Decimal
    category_id: str
    attributes: dict
