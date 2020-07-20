from typing import List, TYPE_CHECKING

from illuin_inject.provider import Provider
from illuin_inject.providers.provider_registry import ProviderRegistry
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .providers_factory import ProvidersFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


class FromCacheProvidersFactory(ProvidersFactory):
    """Returns Providers for targets that are already in the registry."""

    def __init__(self, provider_registry: ProviderRegistry) -> None:
        self._provider_registry = provider_registry

    def accept(self, target: Target[InjectedT]) -> bool:
        return len(self._provider_registry.get_providers(target)) > 0

    def create(self, target: Target[InjectedT], providers_creator: "ProvidersCreator") -> List[Provider[InjectedT]]:
        return self._provider_registry.get_providers(target)
