from typing import Any, cast, TYPE_CHECKING

from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.exceptions import IncompatibleAdapter, NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.scopes import Scope
from opyoid.target import Target
from opyoid.utils import InjectedT
from .list_provider import ListProvider
from .multi_binding import MultiBinding
from ..registered_binding import RegisteredBinding
from ..registered_multi_binding import RegisteredMultiBinding

if TYPE_CHECKING:
    from opyoid.providers.providers_factories.from_registered_binding_provider_factory import (
        FromRegisteredBindingProviderFactory,
    )


class MultiBindingToProviderAdapter(BindingToProviderAdapter):
    """Creates a Provider from an MultiBinding."""

    def __init__(self, item_provider_factory: "FromRegisteredBindingProviderFactory") -> None:
        self._item_provider_factory = item_provider_factory

    def create(self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]) -> Provider[Any]:
        if not isinstance(binding, RegisteredMultiBinding):
            raise IncompatibleAdapter

        multi_registered_binding = binding

        item_providers = []
        for sub_binding in multi_registered_binding.item_bindings:
            new_context: InjectionContext[Any] = context.get_child_context(
                Target(sub_binding.target.type, sub_binding.target.named)
            )
            item_providers.append(self._item_provider_factory.create(sub_binding, new_context, cache_provider=False))

        unscoped_provider = ListProvider(item_providers)
        multi_binding = cast(MultiBinding[Any], multi_registered_binding.raw_binding)
        scope_context: InjectionContext[Scope] = context.get_child_context(Target(multi_binding.scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(
                f"Could not create a provider for {binding!r}: they are no bindings for"
                f" {multi_binding.scope.__name__!r}"
            ) from None
        return scope_provider.get().get_scoped_provider(unscoped_provider)
