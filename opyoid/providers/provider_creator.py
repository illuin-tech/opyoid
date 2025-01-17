import logging
from threading import RLock
from typing import List

from opyoid.exceptions import IncompatibleProviderFactory, NoBindingFound
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .providers_factories import (
    FromBindingProviderFactory,
    FromCacheProviderFactory,
    FromEnvVarProviderFactory,
    JitProviderFactory,
    ListFromItemsProviderFactory,
    ListProviderFactory,
    ProviderFactory,
    ProviderProviderFactory,
    SetProviderFactory,
    TupleProviderFactory,
    TypeProviderFactory,
    UnionProviderFactory,
)


class ProviderCreator:
    """Creates Providers and saves them in the ProviderRegistry."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._provider_factories: List[ProviderFactory] = [
            FromCacheProviderFactory(),
            FromEnvVarProviderFactory(),
            FromBindingProviderFactory(),
            ListProviderFactory(),
            ListFromItemsProviderFactory(),
            SetProviderFactory(),
            TupleProviderFactory(),
            UnionProviderFactory(),
            TypeProviderFactory(),
            ProviderProviderFactory(),
            JitProviderFactory(),
        ]
        self._lock = RLock()

    def get_provider(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        with self._lock:
            provider = self._get_provider(context)
            context.injection_state.provider_registry.set_provider(context.target, provider)
            return provider

    def _get_provider(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        for provider_factory in self._provider_factories:
            try:
                return provider_factory.create(context)
            except IncompatibleProviderFactory:
                pass
        raise NoBindingFound(f"Could not find any bindings for {context.target!r}")
