from typing import List, TYPE_CHECKING

from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT

if TYPE_CHECKING:
    from illuin_inject.providers import ProvidersCreator


class ProvidersFactory:
    """Creates provider for each target.

    A target corresponds to either a Binding target or a dependency of a Binding target.
    """

    def accept(self, target: Target[InjectedT]) -> bool:
        """Returns True if this factory can handle this target."""
        raise NotImplementedError

    def create(self, target: Target[InjectedT], providers_creator: "ProvidersCreator") -> List[Provider[InjectedT]]:
        """Returns providers corresponding to this target."""
        raise NotImplementedError
