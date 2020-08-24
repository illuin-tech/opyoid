import logging
from threading import RLock
from typing import List

from opyoid.exceptions import NoBindingFound
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .providers_factories import FromBindingProviderFactory, FromCacheProviderFactory, OptionalProviderFactory, \
    ProviderFactory, ProviderProviderFactory, SetProviderFactory, TupleProviderFactory, TypeProviderFactory
from .providers_factories.jit_provider_factory import JitProviderFactory
from .providers_factories.list_provider_factory import ListProviderFactory


class ProviderCreator:
    """Creates Providers and saves them in the ProviderRegistry."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._provider_factories: List[ProviderFactory] = [
            FromCacheProviderFactory(),
            FromBindingProviderFactory(),
            ListProviderFactory(),
            SetProviderFactory(),
            TupleProviderFactory(),
            OptionalProviderFactory(),
            TypeProviderFactory(),
            ProviderProviderFactory(),
            JitProviderFactory(),
        ]
        self._lock = RLock()

    def get_provider(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        with self._lock:
            provider = self._get_provider(target, state)
            state.provider_registry.set_provider(target, provider)
            return provider

    def _get_provider(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        for provider_factory in self._provider_factories:
            if provider_factory.accept(target, state):
                return provider_factory.create(target, state)
        raise NoBindingFound(f"Could not find any bindings for {target}")
