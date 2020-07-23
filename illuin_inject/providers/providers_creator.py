import logging
from threading import RLock
from typing import List

from illuin_inject.bindings import BindingRegistry
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .provider_registry import ProviderRegistry
from .providers_factories import FromBindingProviderFactory, FromCacheProviderFactory, OptionalProviderFactory, \
    ProviderFactory, SetProviderFactory, TupleProviderFactory, TypeProviderFactory
from .providers_factories.list_provider_factory import ListProviderFactory


class ProviderCreator:
    """Creates Providers and saves them in the ProviderRegistry."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry
        self._provider_registry = ProviderRegistry()
        self._provider_factories: List[ProviderFactory] = [
            FromCacheProviderFactory(self._provider_registry),
            FromBindingProviderFactory(self._binding_registry),
            ListProviderFactory(),
            SetProviderFactory(),
            TupleProviderFactory(),
            OptionalProviderFactory(),
            TypeProviderFactory(self._binding_registry),
        ]
        self._lock = RLock()

    def get_provider(self, target: Target[InjectedT]) -> Provider[InjectedT]:
        with self._lock:
            provider = self._get_provider(target)
            self._provider_registry.set_provider(target, provider)
            return provider

    def _get_provider(self, target: Target[InjectedT]) -> Provider[InjectedT]:
        for provider_factory in self._provider_factories:
            if provider_factory.accept(target):
                return provider_factory.create(target, self)
        raise NoBindingFound(f"Could not find any bindings for {target}")
