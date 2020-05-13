from typing import List, TYPE_CHECKING

from illuin_inject.dependency_graph import BindingNode
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class BindingNodesFactory:  # pragma: nocover
    """Creates binding nodes for each target.

    A target corresponds to either a Binding target or a dependency of a Binding target.
    """

    def accept(self, target: Target[InjectedT]) -> bool:
        """Return True if this factory can handle this target."""
        raise NotImplementedError

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        """Returns binding nodes corresponding to this target."""
        raise NotImplementedError
