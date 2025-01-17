from typing import Any, cast, List

from opyoid.bindings import ListProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory
from ...exceptions import IncompatibleProviderFactory, NoBindingFound


class ListFromItemsProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target list items providers."""

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if not TypeChecker.is_list(context.target.type):
            raise IncompatibleProviderFactory
        item_providers: List[Provider[Any]] = []
        first_item_type = context.target.type.__args__[0]  # type: ignore[union-attr]
        if TypeChecker.is_union(first_item_type):
            item_types = first_item_type.__args__
        else:
            item_types = [first_item_type]

        for item_target_type in item_types:
            new_target: Target[Any] = Target(item_target_type, context.target.named)
            new_context = context.get_child_context(new_target)
            try:
                item_providers.append(new_context.get_provider())
            except NoBindingFound:
                pass
        if not item_providers:
            raise NoBindingFound(f"No binding found for list items of type {context.target}")
        return cast(Provider[InjectedT], ListProvider(item_providers))
