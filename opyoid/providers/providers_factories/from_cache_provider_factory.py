from typing import cast

from opyoid.exceptions import IncompatibleProviderFactory
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class FromCacheProviderFactory(ProviderFactory):
    """Returns Providers for targets that are already in the registry."""

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if context.target in context.injection_state.provider_registry:
            return cast(Provider[InjectedT], context.injection_state.provider_registry.get_provider(context.target))
        raise IncompatibleProviderFactory
