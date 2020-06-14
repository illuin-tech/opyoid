from typing import TYPE_CHECKING

from illuin_inject.provider import Provider
from illuin_inject.providers.provider_registry import ProviderRegistry
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProviderCreator


class FromCacheProviderFactory(ProviderFactory):
    """Returns Providers for targets that are already in the registry."""

    def __init__(self, provider_registry: ProviderRegistry) -> None:
        self._provider_registry = provider_registry

    def accept(self, target: Target[InjectedT]) -> bool:
        return target in self._provider_registry

    def create(self, target: Target[InjectedT], provider_creator: "ProviderCreator") -> Provider[InjectedT]:
        return self._provider_registry.get_provider(target)
