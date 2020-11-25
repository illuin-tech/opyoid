from typing import TYPE_CHECKING

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .list_provider import ListProvider
from .multi_binding import MultiBinding

if TYPE_CHECKING:
    from opyoid.providers.providers_factories.from_registered_binding_provider_factory \
        import FromRegisteredBindingProviderFactory
    from opyoid.bindings.registered_multi_binding import RegisteredMultiBinding


# pylint: disable=no-self-use, unused-argument
class MultiBindingToProviderAdapter(BindingToProviderAdapter[MultiBinding]):
    """Creates a Provider from an MultiBinding."""

    def __init__(self, item_provider_factory: "FromRegisteredBindingProviderFactory") -> None:
        self._item_provider_factory = item_provider_factory

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, MultiBinding)

    def create(self, binding: "RegisteredMultiBinding[InjectedT]", state: InjectionState) -> Provider[InjectedT]:
        unscoped_provider = ListProvider(
            [
                self._item_provider_factory.create(sub_binding, state, cache_provider=False)
                for sub_binding in binding.item_bindings
            ]
        )
        try:
            scope_provider = state.provider_creator.get_provider(Target(binding.raw_binding.scope), state)
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding!r}: they are no bindings for"
                                         f" {binding.raw_binding.scope.__name__!r}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
