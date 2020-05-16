from typing import List, TYPE_CHECKING

from illuin_inject.dependency_graph import BindingNode, DependencyGraph
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding_nodes_factory import BindingNodesFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class FromCacheBindingNodesFactory(BindingNodesFactory):
    """Returns binding nodes for targets that are already in the dependency graph."""

    def __init__(self, dependency_graph: DependencyGraph) -> None:
        self._dependency_graph = dependency_graph

    def accept(self, target: Target[InjectedT]) -> bool:
        return target in self._dependency_graph.binding_nodes_by_target

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        return self._dependency_graph.binding_nodes_by_target[target]
