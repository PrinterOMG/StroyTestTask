from dataclasses import dataclass
from decimal import Decimal
import datetime as dt


@dataclass(slots=True)
class ProductEntity:
    id: str
    created_at: dt.datetime
    name: str
    description: str
    price: Decimal
    stock: Decimal
    unit: str
    unit_size: Decimal
    category_id: str
    attributes: dict
