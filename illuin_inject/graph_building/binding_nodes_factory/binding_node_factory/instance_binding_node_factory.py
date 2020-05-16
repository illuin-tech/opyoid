from typing import TYPE_CHECKING

from illuin_inject.bindings import Binding, InstanceBinding
from illuin_inject.dependency_graph import BindingNode, InstanceBindingNode
from illuin_inject.typings import InjectedT
from .binding_node_factory import BindingNodeFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


# pylint: disable=no-self-use, unused-argument
class InstanceBindingNodeFactory(BindingNodeFactory[InstanceBinding]):
    """Creates a binding node from an InstanceBinding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, InstanceBinding)

    def create(self, binding: InstanceBinding[InjectedT], graph_builder: "GraphBuilder") -> BindingNode:
        return InstanceBindingNode(binding)
