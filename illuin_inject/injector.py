from typing import Dict, List, Optional, Type

from .binding_registry import BindingRegistry
from .binding_spec import BindingSpec
from .bindings import Binding, ClassBinding, InstanceBinding
from .dependency_graph import DependencyGraph, SimpleBindingNode
from .graph_builder import GraphBuilder
from .object_provider import ObjectProvider
from .scopes import ImmediateScope, PerLookupScope, Scope, SingletonScope, ThreadScope
from .target import Target
from .typings import InjectedT


class Injector:
    """Injection entrypoint.

    Creates the dependency graph and injects types.
    """

    def __init__(self,
                 binding_specs: List[BindingSpec] = None,
                 bindings: List[Binding] = None,
                 scopes_by_type: Dict[Type[Scope], Scope] = None,
                 binding_registry: BindingRegistry = None) -> None:
        self._scopes_by_type: Dict[Type[Scope], Scope] = {
            ImmediateScope: ImmediateScope(),
            SingletonScope: SingletonScope(),
            ThreadScope: ThreadScope(),
            PerLookupScope: PerLookupScope(),
            **(scopes_by_type or {})
        }
        self._binding_registry: BindingRegistry = binding_registry or BindingRegistry()
        self._binding_registry.register(InstanceBinding(self.__class__, self))
        for binding_spec in binding_specs or []:
            binding_spec.configure()
            self._binding_registry.update(binding_spec.binding_registry)
        for binding in bindings or []:
            self._binding_registry.register(binding)
        graph_builder = GraphBuilder(self._binding_registry, self._scopes_by_type.keys())
        dependency_graph = graph_builder.get_dependency_graph()
        self._provider = ObjectProvider(dependency_graph, self._scopes_by_type)
        self._instantiate_immediate_scoped_bindings(dependency_graph)

    def _instantiate_immediate_scoped_bindings(self, dependency_graph: DependencyGraph) -> None:
        for binding_nodes in dependency_graph.binding_nodes_by_target.values():
            for binding_node in binding_nodes:
                if isinstance(binding_node, SimpleBindingNode) \
                    and isinstance(binding_node.binding, ClassBinding) \
                    and binding_node.binding.scope == ImmediateScope:
                    self._provider.provide_from_binding_node(binding_node)

    def inject(self, target_type: Type[InjectedT], annotation: Optional[str] = None) -> InjectedT:
        return self._provider.provide(Target(target_type, annotation))
