import logging
from typing import Callable, Collection, Dict, Iterable, Type, Union, cast

from .bindings import ClassBinding, InstanceBinding
from .dependency_graph import BindingNode, CollectionBindingNode, DependencyGraph, SimpleBindingNode
from .exceptions import NoBindingFound
from .scopes import Scope
from .target import Target
from .type_checker import TypeChecker
from .typings import InjectedT


class ObjectProvider:
    logger = logging.getLogger(__name__)

    def __init__(self, dependency_graph: DependencyGraph, scopes_by_type: Dict[Type[Scope], Scope]):
        self._dependency_graph = dependency_graph
        self._scopes_by_type = scopes_by_type

    def provide(self, target: Target[InjectedT]) -> InjectedT:
        return self._provide(target)

    def _provide(self,
                 target: Target[InjectedT],
                 collection_constructor: Callable[[Iterable], Collection] = None) -> InjectedT:
        if target in self._dependency_graph.binding_nodes_by_target:
            binding_nodes = self._dependency_graph.binding_nodes_by_target[target]
            if collection_constructor:
                return collection_constructor(
                    self.provide_from_binding_node(binding_node)
                    for binding_node in binding_nodes
                )
            return self.provide_from_binding_node(binding_nodes[-1])
        if TypeChecker.is_list(target.type):
            return self._provide(Target(target.type.__args__[0], target.annotation), list)
        if TypeChecker.is_set(target.type):
            return self._provide(Target(target.type.__args__[0], target.annotation), set)
        if TypeChecker.is_tuple(target.type):
            return self._provide(Target(target.type.__args__[0], target.annotation), tuple)
        if TypeChecker.is_type(target.type):
            return self._provide_type(Target(target.type.__args__[0], target.annotation), collection_constructor)
        raise NoBindingFound(f"Could not find binding for {target}")

    # pylint: disable=unsubscriptable-object
    def _provide_type(self,
                      target: Target,
                      collection_constructor: Callable[[Iterable], Collection] = None,
                      ) -> Union[Type[InjectedT], Collection[Type[InjectedT]]]:
        bindings = [
            binding_node.binding
            for binding_node in self._dependency_graph.binding_nodes_by_target.get(target, [])
            if isinstance(binding_node, SimpleBindingNode) and isinstance(binding_node.binding, ClassBinding)
        ]

        if not bindings:
            raise NoBindingFound(f"Could not find binding for Type[{target.type}]")

        if collection_constructor:
            return collection_constructor(
                binding.bound_type
                for binding in bindings
            )
        return bindings[-1].bound_type

    def provide_from_binding_node(self, binding_node: BindingNode) -> InjectedT:
        if isinstance(binding_node, CollectionBindingNode):
            return binding_node.collection_constructor(
                self.provide_from_binding_node(binding_node)
                for binding_node in binding_node.sub_bindings
            )
        binding_node = cast(SimpleBindingNode, binding_node)
        binding = binding_node.binding
        if isinstance(binding, InstanceBinding):
            return binding.bound_instance
        binding = cast(ClassBinding, binding)
        scope = self._scopes_by_type[binding.scope]
        return scope.get(binding.bound_type, lambda: self._get_instance(binding_node))

    def _get_instance(self, binding_node: SimpleBindingNode[ClassBinding[InjectedT]]) -> InjectedT:
        args = [
            self.provide_from_binding_node(parameter_node.binding_node)
            for parameter_node in binding_node.args
        ]
        kwargs = {
            parameter_node.parameter.name: self.provide_from_binding_node(parameter_node.binding_node)
            for parameter_node in binding_node.kwargs
        }
        return binding_node.binding.bound_type(*args, **kwargs)
