from typing import Dict, List, Type

from illuin_inject.scopes import PerLookupScope, SingletonScope, ThreadScope
from .binding_registry import BindingRegistry
from .binding_spec import BindingSpec
from .bindings import Binding, InstanceBinding
from .graph_builder import GraphBuilder
from .object_provider import ObjectProvider
from .scopes import Scope
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
            SingletonScope: SingletonScope(),
            ThreadScope: ThreadScope(),
            PerLookupScope: PerLookupScope(),
            **(scopes_by_type or {})
        }
        self._binding_registry = binding_registry or BindingRegistry()
        self._binding_registry.register(InstanceBinding(self.__class__, self))
        for binding_spec in binding_specs or []:
            binding_spec.configure()
            self._binding_registry.update(binding_spec.binding_registry)
        for binding in bindings or []:
            self._binding_registry.register(binding)
        graph_builder = GraphBuilder(self._binding_registry, self._scopes_by_type.keys())
        dependency_graph = graph_builder.get_dependency_graph()
        self._provider = ObjectProvider(dependency_graph, self._scopes_by_type)

    def inject(self, target_type: Type[InjectedT]) -> InjectedT:
        return self._provider.provide(target_type)
