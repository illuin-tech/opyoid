import logging
from typing import Callable, Optional, Type

from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
from .from_callable_provider import FromCallableProvider
from .parameters_provider import ParametersProvider
from ...scopes import Scope


class CallableToProviderAdapter:
    """Creates a Provider from a callable."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._parameters_provider = ParametersProvider()

    def create(
        self,
        type_or_function: Callable[..., InjectedT],
        context: InjectionContext[InjectedT],
        scope: Type[Scope],
    ) -> Provider[InjectedT]:
        cached_provider: Optional[Provider[InjectedT]] = context.injection_state.provider_registry.get_provider(
            context.target
        )
        if cached_provider:
            return cached_provider

        (
            positional_providers,
            args_provider,
            keyword_providers,
        ) = self._parameters_provider.get_parameters_provider(type_or_function, context)
        unscoped_provider = FromCallableProvider(
            type_or_function,
            positional_providers,
            args_provider,
            keyword_providers,
            context,
        )
        scope_context: InjectionContext[Scope] = context.get_child_context(Target(scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(
                f"Could not create a provider for {type_or_function!r}: they are no bindings for {scope.__name__!r}"
            ) from None
        provider = scope_provider.get().get_scoped_provider(unscoped_provider)
        context.injection_state.provider_registry.set_provider(context.target, provider)
        return provider
