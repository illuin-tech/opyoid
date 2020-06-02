from typing import List, TYPE_CHECKING

from illuin_inject.providers.list_provider import ListProvider
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .providers_factory import ProvidersFactory

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


class ListProvidersFactory(ProvidersFactory):
    """Creates a Provider that groups the target list items providers."""

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_list(target.type)

    def create(self,
               target: Target[List[InjectedT]],
               providers_creator: "ProvidersCreator") -> List[Provider[List[InjectedT]]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return [
            ListProvider(providers_creator.get_providers(new_target))
        ]
