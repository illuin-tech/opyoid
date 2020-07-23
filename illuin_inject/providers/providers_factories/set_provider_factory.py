from typing import List, Set, TYPE_CHECKING

from illuin_inject.bindings.class_binding import FromClassProvider
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProviderCreator


class SetProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target set items providers."""

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_set(target.type)

    def create(self,
               target: Target[Set[InjectedT]],
               provider_creator: "ProviderCreator") -> Provider[Set[InjectedT]]:
        new_target = Target(List[target.type.__args__[0]], target.annotation)
        return FromClassProvider(set, [provider_creator.get_provider(new_target)], {})
