from typing import TYPE_CHECKING

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.instance_binding import InstanceBinding
from opyoid.bindings.provider_binding import ProviderBinding
from opyoid.bindings.self_binding import SelfBinding
from opyoid.exceptions import BindingError, NoBindingFound, NonInjectableTypeError
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import EMPTY, InjectedT
from .item_binding import ItemBinding
from .list_provider import ListProvider
from .multi_binding import MultiBinding

if TYPE_CHECKING:
    from opyoid.providers.providers_factories import FromBindingProviderFactory


# pylint: disable=no-self-use, unused-argument
class MultiBindingToProviderAdapter(BindingToProviderAdapter[MultiBinding]):
    """Creates a Provider from an MultiBinding."""

    def __init__(self, item_provider_factory: "FromBindingProviderFactory") -> None:
        self._item_provider_factory = item_provider_factory

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, MultiBinding)

    def create(self, binding: MultiBinding[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        unscoped_provider = ListProvider(
            [
                self._get_item_provider(binding, item_binding, state)
                for item_binding in binding.item_bindings
            ]
        )
        try:
            scope_provider = state.provider_creator.get_provider(Target(binding.scope), state)
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding!r}: they are no bindings for"
                                         f" {binding.scope.__name__!r}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)

    def _get_item_provider(self,
                           parent_binding: MultiBinding[InjectedT],
                           item_binding: ItemBinding[InjectedT],
                           state: InjectionState) -> Provider[InjectedT]:
        if item_binding.bound_type is not EMPTY:
            item_binding = SelfBinding(
                item_binding.bound_type,
                parent_binding.scope,
                parent_binding.annotation,
            )
        elif item_binding.bound_instance is not EMPTY:
            item_binding = InstanceBinding(
                parent_binding.target_type,
                item_binding.bound_instance,
                parent_binding.annotation,
            )
        elif item_binding.bound_provider is not EMPTY:
            item_binding = ProviderBinding(
                parent_binding.target_type,
                item_binding.bound_provider,
                parent_binding.scope,
                parent_binding.annotation,
            )
        else:
            raise BindingError(
                f"ItemBinding in {parent_binding!r} has no instance, class or provider, one should be set")

        return self._item_provider_factory.create_from_binding(item_binding, state)
