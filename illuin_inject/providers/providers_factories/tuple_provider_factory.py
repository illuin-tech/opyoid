from typing import List, Tuple

from illuin_inject.bindings import FromClassProvider
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory


class TupleProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target tuple items providers."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_tuple(target.type)

    def create(self,
               target: Target[Tuple[InjectedT]],
               state: InjectionState) -> Provider[Tuple[InjectedT]]:
        new_target = Target(List[target.type.__args__[0]], target.annotation)
        return FromClassProvider(tuple, [state.provider_creator.get_provider(new_target, state)], None, {})
