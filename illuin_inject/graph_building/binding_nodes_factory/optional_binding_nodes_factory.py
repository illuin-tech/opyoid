from typing import List, TYPE_CHECKING

from illuin_inject.dependency_graph import BindingNode
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .binding_nodes_factory import BindingNodesFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class OptionalBindingNodesFactory(BindingNodesFactory):
    """Returns the binding nodes for an optional type target."""

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_optional(target.type)

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return graph_builder.get_and_save_binding_nodes(new_target)
