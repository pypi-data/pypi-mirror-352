from collections.abc import Mapping

import requests

from .types import ItemData, RecipesData, UsesData, LineageData


Params = Mapping[str, int | bool | str | None]


class Infinibrowser:
    """
    Infinibrowser Client
    """

    # Base URL for the API
    API_URL = "https://infinibrowser.wiki/"

    @classmethod
    def _get_request(cls, path: str, params: Params | None = None):
        url = f"{cls.API_URL}{path}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_item(cls, id: str):
        """
        Get information about the item
        """

        path = "/api/item"
        params = {"id": id}

        data = cls._get_request(path=path, params=params)

        return ItemData(**data)

    @classmethod
    def get_recipes(cls, id: str, offset=0):
        """
        Get recipes for the item
        """

        path = "/api/recipes"
        params = {"id": id, "offset": offset}

        data = cls._get_request(path=path, params=params)

        return RecipesData(**data)

    @classmethod
    def get_uses(cls, id: str, offset=0):
        """
        Get uses for the item
        """

        path = "/api/uses"
        params = {"id": id, "offset": offset}

        data = cls._get_request(path=path, params=params)

        return UsesData(**data)

    @classmethod
    def get_lineage(cls, id: str):
        """
        Get lineage for the item
        """

        path = "/api/recipe"
        params = {"id": id}

        data = cls._get_request(path=path, params=params)

        return LineageData(**data)
