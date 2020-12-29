from typing import TYPE_CHECKING

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
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

    def accept(self, binding: Binding[InjectedT], context: InjectionContext[InjectedT]) -> bool:
        return isinstance(binding, MultiBinding)

    def create(self,
               binding: "RegisteredMultiBinding[InjectedT]",
               context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        item_providers = []
        for sub_binding in binding.item_bindings:
            new_context = context.get_child_context(Target(sub_binding.target.type, sub_binding.target.named))
            item_providers.append(self._item_provider_factory.create(sub_binding, new_context, cache_provider=False))

        unscoped_provider = ListProvider(item_providers)

        scope_context = context.get_child_context(Target(binding.raw_binding.scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding!r}: they are no bindings for"
                                         f" {binding.raw_binding.scope.__name__!r}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
