from pydantic import BaseModel

from .items import Element


class SearchData(BaseModel):
    chunk_size: int
    items: list[Element]
