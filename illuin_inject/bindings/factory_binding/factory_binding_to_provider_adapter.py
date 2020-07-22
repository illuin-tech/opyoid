from typing import TYPE_CHECKING

from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .factory_binding import FactoryBinding
from .from_factory_provider import FromFactoryProvider

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


# pylint: disable=no-self-use
class FactoryBindingToProviderAdapter(BindingToProviderAdapter[FactoryBinding]):
    """Creates a Provider from an FactoryBinding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, FactoryBinding)

    def create(self, binding: FactoryBinding[InjectedT], providers_creator: "ProvidersCreator") -> Provider[InjectedT]:
        factory_provider = providers_creator.get_providers(
            Target(binding.bound_factory, binding.annotation)
        )[-1]
        unscoped_provider = FromFactoryProvider(
            factory_provider,
        )
        try:
            scope_provider = providers_creator.get_providers(Target(binding.scope))[-1]
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding}: they are no bindings for"
                                         f"the scope {binding.scope}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
