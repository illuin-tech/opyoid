from typing import List

from illuin_inject.typings import InjectedT
from illuin_inject.provider import Provider


class ListProvider(Provider[List[InjectedT]]):
    """Provides a list from a list of providers."""

    def __init__(self, item_providers: List[Provider[InjectedT]]) -> None:
        self._item_providers = item_providers

    def get(self) -> List[InjectedT]:
        return [
            item_provider.get()
            for item_provider in self._item_providers
        ]
