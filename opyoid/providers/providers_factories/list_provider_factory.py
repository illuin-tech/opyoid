from typing import List

from opyoid.bindings import ListProvider
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.typings import InjectedT
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
