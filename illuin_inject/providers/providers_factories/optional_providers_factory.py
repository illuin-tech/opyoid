from typing import List, Optional, TYPE_CHECKING

from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .providers_factory import ProvidersFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


class OptionalProvidersFactory(ProvidersFactory):
    """Returns the Provider for an optional type target."""

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_optional(target.type)

    def create(self,
               target: Target[Optional[InjectedT]],
               providers_creator: "ProvidersCreator") -> List[Provider[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return providers_creator.get_providers(new_target)
