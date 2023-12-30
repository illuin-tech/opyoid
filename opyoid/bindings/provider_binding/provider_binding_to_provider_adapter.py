from typing import cast, Type

from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter, NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.scopes import Scope
from opyoid.target import Target
from opyoid.utils import InjectedT
from .from_provider_provider import FromProviderProvider
from .provider_binding import ProviderBinding
from ..self_binding import CallableToProviderAdapter


class ProviderBindingToProviderAdapter(BindingToProviderAdapter):
    """Creates a Provider from a ProviderBinding."""

    def __init__(self) -> None:
        BindingToProviderAdapter.__init__(self)
        self._adapter = CallableToProviderAdapter()

    def create(
        self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        if not isinstance(binding.raw_binding, ProviderBinding):
            raise IncompatibleAdapter
        if isinstance(binding.raw_binding.bound_provider, Provider):
            return binding.raw_binding.bound_provider
        if not isinstance(binding.raw_binding.bound_provider, type):
            context.target.provider_cache_key = binding.raw_binding.bound_provider
            return self._adapter.create(binding.raw_binding.bound_provider, context, binding.raw_binding.scope)
        bound_provider = cast(Type[Provider[InjectedT]], binding.raw_binding.bound_provider)
        provider_target: Target[Provider[InjectedT]] = Target(bound_provider, binding.raw_binding.named)
        provider_context = context.get_child_context(provider_target)
        provider_provider = provider_context.get_provider()
        unscoped_provider = FromProviderProvider(
            provider_provider,
        )
        scope_context: InjectionContext[Scope] = context.get_child_context(Target(binding.raw_binding.scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(
                f"Could not create a provider for {binding}: they are no bindings for"
                f"the scope {binding.raw_binding.scope}"
            ) from None
        return scope_provider.get().get_scoped_provider(unscoped_provider)
