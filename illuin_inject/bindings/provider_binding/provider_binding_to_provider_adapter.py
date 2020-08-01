from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .from_provider_provider import FromProviderProvider
from .provider_binding import ProviderBinding


# pylint: disable=no-self-use, unused-argument
class ProviderBindingToProviderAdapter(BindingToProviderAdapter[ProviderBinding]):
    """Creates a Provider from a ProviderBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, ProviderBinding)

    def create(self, binding: ProviderBinding[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        if isinstance(binding.bound_provider, Provider):
            return binding.bound_provider
        provider_provider = state.provider_creator.get_provider(
            Target(binding.bound_provider, binding.annotation),
            state,
        )
        unscoped_provider = FromProviderProvider(
            provider_provider,
        )
        try:
            scope_provider = state.provider_creator.get_provider(Target(binding.scope), state)
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding}: they are no bindings for"
                                         f"the scope {binding.scope}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
