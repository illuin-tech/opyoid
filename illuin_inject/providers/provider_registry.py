from typing import Dict

from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT


class ProviderRegistry:
    """Stores Providers for each Target to create a cache."""

    def __init__(self):
        self._provider_by_target: Dict[Target, Provider] = {}

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return item in self._provider_by_target

    def set_provider(self, target: Target[InjectedT], provider: Provider[InjectedT]) -> None:
        self._provider_by_target[target] = provider

    def get_provider(self, target: Target[InjectedT]) -> Provider[InjectedT]:
        return self._provider_by_target.get(target, [])
