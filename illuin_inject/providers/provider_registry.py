from typing import Dict, List

from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from illuin_inject.provider import Provider


class ProviderRegistry:
    """Stores Providers for each Target to create a cache."""

    def __init__(self):
        self._providers_by_target: Dict[Target, List[Provider]] = {}

    def set_providers(self, target: Target[InjectedT], providers: List[Provider[InjectedT]]) -> None:
        self._providers_by_target[target] = providers

    def get_providers(self, target: Target[InjectedT]) -> List[Provider[InjectedT]]:
        return self._providers_by_target.get(target, [])
