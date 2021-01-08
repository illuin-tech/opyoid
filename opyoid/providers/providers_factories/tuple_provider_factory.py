from typing import List, Tuple

from opyoid.bindings import FromClassProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class TupleProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target tuple items providers."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_tuple(context.target.type)

    def create(self, context: InjectionContext[Tuple[InjectedT]]) -> Provider[Tuple[InjectedT]]:
        new_target = Target(List[context.target.type.__args__[0]], context.target.named)
        new_context = context.get_child_context(new_target)
        return FromClassProvider(tuple, [new_context.get_provider()], None, {})
