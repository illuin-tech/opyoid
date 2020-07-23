import logging
from typing import List, TYPE_CHECKING

from illuin_inject.bindings import Binding, BindingRegistry, BindingToProviderAdapter, ClassBindingToProviderAdapter, \
    FactoryBindingToProviderAdapter, InstanceBindingToProviderAdapter, MultiBindingToProviderAdapter
from illuin_inject.exceptions import BindingError
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProviderCreator


class FromBindingProviderFactory(ProviderFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry
        self._binding_to_provider_adapters: List[BindingToProviderAdapter] = [
            InstanceBindingToProviderAdapter(),
            ClassBindingToProviderAdapter(),
            FactoryBindingToProviderAdapter(),
            MultiBindingToProviderAdapter(self),
        ]

    def accept(self, target: Target[InjectedT]) -> bool:
        return target in self._binding_registry

    def create(self, target: Target[InjectedT], provider_creator: "ProviderCreator") -> Provider[InjectedT]:
        binding = self._binding_registry.get_binding(target)
        return self.create_from_binding(binding, provider_creator)

    def create_from_binding(self,
                            binding: Binding[InjectedT],
                            providers_creator: "ProviderCreator") -> Provider[InjectedT]:
        for adapter in self._binding_to_provider_adapters:
            if adapter.accept(binding):
                return adapter.create(binding, providers_creator)
        raise BindingError(f"Could not find a BindingToProviderAdapter for {binding!r}")
