from typing import List

from opyoid.provider import Provider
from opyoid.utils import InjectedT


class ListProvider(Provider[List[InjectedT]]):
    def __init__(self, item_providers: List[Provider[InjectedT]]) -> None:
        self._item_providers = item_providers

    def get(self) -> List[InjectedT]:
        return [
            provider.get()
            for provider in self._item_providers
        ]
