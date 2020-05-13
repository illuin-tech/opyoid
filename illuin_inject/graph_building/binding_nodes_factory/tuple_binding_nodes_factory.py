from typing import List, TYPE_CHECKING

from illuin_inject.dependency_graph import BindingNode, CollectionBindingNode
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .binding_nodes_factory import BindingNodesFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class TupleBindingNodesFactory(BindingNodesFactory):
    """Creates a CollectionBindingNode that groups the target tuple items binding nodes."""

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_tuple(target.type)

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return [CollectionBindingNode(graph_builder.get_and_save_binding_nodes(new_target), tuple)]
