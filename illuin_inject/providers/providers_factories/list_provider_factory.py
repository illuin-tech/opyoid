from typing import List

from illuin_inject.bindings import ListProvider
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory


class ListProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target set items providers."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_list(target.type)

    def create(self,
               target: Target[List[InjectedT]],
               state: InjectionState) -> Provider[List[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return ListProvider([state.provider_creator.get_provider(new_target, state)])
