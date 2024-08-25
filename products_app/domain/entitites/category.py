from dataclasses import dataclass
import datetime as dt


@dataclass(slots=True)
class CategoryEntity:
    id: str
    created_at: dt.datetime
    name: str
    parent_category_id: str | None


@dataclass(slots=True)
class ExtendedCategoryEntity(CategoryEntity):
    sub_categories: list['ExtendedCategoryEntity']
