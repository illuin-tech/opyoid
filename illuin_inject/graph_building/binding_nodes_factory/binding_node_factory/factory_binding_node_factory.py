from typing import TYPE_CHECKING

from illuin_inject.bindings import Binding, FactoryBinding
from illuin_inject.dependency_graph import BindingNode, FactoryBindingNode
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding_node_factory import BindingNodeFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


# pylint: disable=no-self-use
class FactoryBindingNodeFactory(BindingNodeFactory[FactoryBinding]):
    """Creates a binding node from a FactoryBinding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, FactoryBinding)

    def create(self, binding: FactoryBinding[InjectedT], graph_builder: "GraphBuilder") -> BindingNode:
        return FactoryBindingNode(
            binding,
            graph_builder.get_and_save_binding_nodes(Target(binding.bound_factory, binding.annotation))[-1],
        )
