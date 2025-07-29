from typing import Literal
from pydantic import BaseModel


class Element(BaseModel):
    id: str
    emoji: str


class ItemData(BaseModel):
    id: int
    text: str
    emoji: str
    use_count: int
    recipe_count: int
    depth: int


Recipe = tuple[Element, Element]


class RecipesData(BaseModel):
    total: int
    recipes: list[Recipe]


class Use(BaseModel):
    pair: Element
    result: Element


class UsesData(BaseModel):
    total: int
    uses: list[Use]


class Step(BaseModel):
    a: Element
    b: Element
    result: Element


Lineage = list[Step]


class LineageData(BaseModel):
    steps: Lineage
    missing: dict[str, str | Literal["loop"]]


__all__ = [
    "Element",
    "ItemData",
    "Recipe",
    "RecipesData",
    "Use",
    "UsesData",
    "Step",
    "Lineage",
    "LineageData",
]
