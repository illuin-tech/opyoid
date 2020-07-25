from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.bindings.instance_binding import FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .factory_binding import FactoryBinding
from .from_factory_provider import FromFactoryProvider


# pylint: disable=no-self-use, unused-argument
class FactoryBindingToProviderAdapter(BindingToProviderAdapter[FactoryBinding]):
    """Creates a Provider from an FactoryBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, FactoryBinding)

    def create(self, binding: FactoryBinding[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        if isinstance(binding.bound_factory, Factory):
            factory_provider = FromInstanceProvider(binding.bound_factory)
        else:
            factory_provider = state.provider_creator.get_provider(
                Target(binding.bound_factory, binding.annotation),
                state,
            )
        unscoped_provider = FromFactoryProvider(
            factory_provider,
        )
        try:
            scope_provider = state.provider_creator.get_provider(Target(binding.scope), state)
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding}: they are no bindings for"
                                         f"the scope {binding.scope}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
