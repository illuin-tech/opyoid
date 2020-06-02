import logging
from threading import RLock
from typing import List

from illuin_inject.bindings import BindingRegistry
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from illuin_inject.provider import Provider
from .provider_registry import ProviderRegistry
from .providers_factories import FromBindingsProvidersFactory, FromCacheProvidersFactory, ListProvidersFactory, \
    OptionalProvidersFactory, ProvidersFactory, SetProvidersFactory, TupleProvidersFactory, TypeProvidersFactory


class ProvidersCreator:
    """Creates Providers and saves them in the ProviderRegistry."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry
        self._provider_registry = ProviderRegistry()
        self._provider_factories: List[ProvidersFactory] = [
            FromCacheProvidersFactory(self._provider_registry),
            FromBindingsProvidersFactory(self._binding_registry),
            ListProvidersFactory(),
            SetProvidersFactory(),
            TupleProvidersFactory(),
            OptionalProvidersFactory(),
            TypeProvidersFactory(self._binding_registry),
        ]
        self._lock = RLock()

    def get_providers(self, target: Target[InjectedT]) -> List[Provider[InjectedT]]:
        with self._lock:
            providers = self._get_providers(target)
            self._provider_registry.set_providers(target, providers)
            return providers

    def _get_providers(self, target: Target[InjectedT]) -> List[Provider[InjectedT]]:
        for provider_factory in self._provider_factories:
            if provider_factory.accept(target):
                return provider_factory.create(target, self)
        raise NoBindingFound(f"Could not find any bindings for {target}")
