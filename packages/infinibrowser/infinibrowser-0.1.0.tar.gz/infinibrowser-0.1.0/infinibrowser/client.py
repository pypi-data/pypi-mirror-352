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

    def __init__(self):
        pass

    def _get_request(self, path: str, params: Params | None = None):
        url = f"{self.API_URL}{path}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_item(self, id: str):
        """
        Get information about the item
        """

        path = "/api/item"
        params = {"id": id}

        data = self._get_request(path=path, params=params)

        return ItemData(**data)

    def get_recipes(self, id: str, offset=0):
        """
        Get recipes for the item
        """

        path = "/api/recipes"
        params = {"id": id, "offset": offset}

        data = self._get_request(path=path, params=params)

        return RecipesData(**data)

    def get_uses(self, id: str, offset=0):
        """
        Get uses for the item
        """

        path = "/api/uses"
        params = {"id": id, "offset": offset}

        data = self._get_request(path=path, params=params)

        return UsesData(**data)

    def get_lineage(self, id: str):
        """
        Get lineage for the item
        """

        path = "/api/recipe"
        params = {"id": id}

        data = self._get_request(path=path, params=params)

        return LineageData(**data)
