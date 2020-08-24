from typing import Optional

from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.typings import InjectedT
from .provider_factory import ProviderFactory


class OptionalProviderFactory(ProviderFactory):
    """Returns the Provider for an optional type target."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_optional(target.type)

    def create(self,
               target: Target[Optional[InjectedT]],
               state: InjectionState) -> Provider[InjectedT]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return state.provider_creator.get_provider(new_target, state)
