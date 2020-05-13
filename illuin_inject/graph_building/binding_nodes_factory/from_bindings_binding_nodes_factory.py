import logging
from typing import Container, List, TYPE_CHECKING, Type

from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import Binding
from illuin_inject.dependency_graph import BindingNode
from illuin_inject.exceptions import BindingError
from illuin_inject.scopes import Scope
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding_node_factory import BindingNodeFactory, ClassBindingNodeFactory, FactoryBindingNodeFactory, \
    InstanceBindingNodeFactory
from .binding_nodes_factory import BindingNodesFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class FromBindingsBindingNodesFactory(BindingNodesFactory):
    """Creates binding nodes, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self,
                 binding_registry: BindingRegistry,
                 scope_types: Container[Type[Scope]],
                 ) -> None:
        self._binding_registry = binding_registry
        self._binding_node_factories: List[BindingNodeFactory] = [
            InstanceBindingNodeFactory(),
            ClassBindingNodeFactory(scope_types),
            FactoryBindingNodeFactory(),
        ]

    def accept(self, target: Target[InjectedT]) -> bool:
        return len(self._binding_registry.get_bindings(target)) > 0

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        return [
            self._get_binding_node_from_binding(binding, graph_builder)
            for binding in self._binding_registry.get_bindings(target)
        ]

    def _get_binding_node_from_binding(self, binding: Binding[InjectedT], graph_builder: "GraphBuilder") -> BindingNode:
        for binding_node_factory in self._binding_node_factories:
            if binding_node_factory.accept(binding):
                return binding_node_factory.create(binding, graph_builder)
        raise BindingError(f"Could not find a BindingNodeFactory for {binding}")
