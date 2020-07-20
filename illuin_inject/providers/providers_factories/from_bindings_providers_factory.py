import logging
from typing import List, TYPE_CHECKING

from illuin_inject.bindings import Binding, BindingRegistry, BindingToProviderAdapter, ClassBindingToProviderAdapter, \
    FactoryBindingToProviderAdapter, InstanceBindingToProviderAdapter
from illuin_inject.exceptions import BindingError
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .providers_factory import ProvidersFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


class FromBindingsProvidersFactory(ProvidersFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry
        self._binding_to_provider_adapters: List[BindingToProviderAdapter] = [
            InstanceBindingToProviderAdapter(),
            ClassBindingToProviderAdapter(),
            FactoryBindingToProviderAdapter(),
        ]

    def accept(self, target: Target[InjectedT]) -> bool:
        return len(self._binding_registry.get_bindings(target)) > 0

    def create(self, target: Target[InjectedT], providers_creator: "ProvidersCreator") -> List[Provider[InjectedT]]:
        return [
            self._get_provider_from_binding(binding, providers_creator)
            for binding in self._binding_registry.get_bindings(target)
        ]

    def _get_provider_from_binding(self,
                                   binding: Binding[InjectedT],
                                   providers_creator: "ProvidersCreator") -> Provider[InjectedT]:
        for adapter in self._binding_to_provider_adapters:
            if adapter.accept(binding):
                return adapter.create(binding, providers_creator)
        raise BindingError(f"Could not find a BindingToProviderAdapter for {binding}")
