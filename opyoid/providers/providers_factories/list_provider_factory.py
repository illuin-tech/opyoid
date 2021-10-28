from typing import List

from opyoid.bindings import ListProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory
from ...exceptions import NoBindingFound


class ListProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target set items providers."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_list(context.target.type)

    def create(self, context: InjectionContext[List[InjectedT]]) -> Provider[List[InjectedT]]:
        item_providers = []
        if TypeChecker.is_union(context.target.type.__args__[0]):
            item_types = context.target.type.__args__[0].__args__
        else:
            item_types = [context.target.type.__args__[0]]

        for item_target_type in item_types:
            new_target = Target(item_target_type, context.target.named)
            new_context = context.get_child_context(new_target)
            try:
                item_providers.append(new_context.get_provider())
            except NoBindingFound:
                pass
        if not item_providers:
            raise NoBindingFound(f"No binding found for list items of type {context.target}")
        return ListProvider(item_providers)
