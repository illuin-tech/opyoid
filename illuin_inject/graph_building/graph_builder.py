import logging
from typing import Container, List, Type

from illuin_inject.binding_registry import BindingRegistry, Target
from illuin_inject.dependency_graph import BindingNode, DependencyGraph
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.scopes import Scope
from illuin_inject.typings import InjectedT
from .binding_nodes_factory import BindingNodesFactory, FromBindingsBindingNodesFactory, FromCacheBindingNodesFactory, \
    ListBindingNodesFactory, OptionalBindingNodesFactory, SetBindingNodesFactory, TupleBindingNodesFactory, \
    TypeBindingNodesFactory


class GraphBuilder:
    """Builds the DependencyGraph."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry, scope_types: Container[Type[Scope]]) -> None:
        self._binding_registry = binding_registry
        self._dependency_graph: DependencyGraph = DependencyGraph()
        self._binding_nodes_factories: List[BindingNodesFactory] = [
            FromCacheBindingNodesFactory(self._dependency_graph),
            FromBindingsBindingNodesFactory(self._binding_registry, scope_types),
            ListBindingNodesFactory(),
            SetBindingNodesFactory(),
            TupleBindingNodesFactory(),
            OptionalBindingNodesFactory(),
            TypeBindingNodesFactory(self._binding_registry),
        ]

    def get_dependency_graph(self) -> DependencyGraph:
        """Main function that builds the dependency graph."""

        for target in self._binding_registry.get_bindings_by_target():
            self.get_and_save_binding_nodes(target)
        return self._dependency_graph

    def get_and_save_binding_nodes(self, target: Target[InjectedT]) -> List[BindingNode]:
        binding_nodes = self._get_binding_nodes(target)
        # pylint: disable=unsupported-assignment-operation
        self._dependency_graph.binding_nodes_by_target[target] = binding_nodes
        return binding_nodes

    def _get_binding_nodes(self, target: Target[InjectedT]) -> List[BindingNode]:
        for binding_nodes_factory in self._binding_nodes_factories:
            if binding_nodes_factory.accept(target):
                return binding_nodes_factory.create(target, self)
        raise NoBindingFound(f"Could not find any bindings for {target}")
