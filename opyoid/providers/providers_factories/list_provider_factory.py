from typing import List

from opyoid.bindings import ListProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class ListProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target set items providers."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_list(context.target.type)

    def create(self, context: InjectionContext[List[InjectedT]]) -> Provider[List[InjectedT]]:
        new_target = Target(context.target.type.__args__[0], context.target.named)
        new_context = context.get_child_context(new_target)
        return ListProvider([new_context.get_provider()])
