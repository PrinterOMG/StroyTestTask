from dataclasses import dataclass


@dataclass(slots=True)
class NewCategoryDTO:
    name: str
    parent_category_id: str | None


@dataclass(slots=True)
class UpdateCategoryDTO:
    id: str
    name: str
    parent_category_id: str
