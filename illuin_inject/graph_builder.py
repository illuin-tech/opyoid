import logging
from inspect import Parameter, signature
from threading import Lock
from typing import Iterable, List, Optional, Type

from .binding_registry import BindingRegistry, Target
from .bindings import Binding, ClassBinding, InstanceBinding
from .dependency_graph import BindingNode, CollectionBindingNode, DependencyGraph, ParameterNode, SimpleBindingNode
from .exceptions import BindingError, NoBindingFound, NonInjectableTypeError
from .scopes import Scope
from .type_checker import TypeChecker
from .typings import InjectedT


class GraphBuilder:
    """Builds the DependencyGraph."""

    logger = logging.getLogger(__name__)

    def __init__(self, binding_registry: BindingRegistry, scope_types: Iterable[Type[Scope]]) -> None:
        self._binding_registry = binding_registry
        self._scope_types = scope_types
        self._dependency_graph: Optional[DependencyGraph] = None
        self._lock = Lock()
        self._current_class_binding: Optional[ClassBinding] = None

    def get_dependency_graph(self) -> DependencyGraph:
        with self._lock:
            self._dependency_graph = DependencyGraph()
            for target in self._binding_registry.get_bindings_by_target():
                self._get_and_save_binding_nodes(target)
            return self._dependency_graph

    def _get_and_save_binding_nodes(self, target: Target[InjectedT]) -> List[BindingNode]:
        binding_nodes = self._get_binding_nodes(target)
        # pylint: disable=unsupported-assignment-operation
        self._dependency_graph.binding_nodes_by_target[target] = binding_nodes
        return binding_nodes

    def _get_binding_nodes(self, target: Target[InjectedT]) -> List[BindingNode]:
        # pylint: disable=unsupported-membership-test,unsubscriptable-object
        if target in self._dependency_graph.binding_nodes_by_target:
            return self._dependency_graph.binding_nodes_by_target[target]
        bindings = self._binding_registry.get_bindings(target)
        if bindings:
            return [self._get_binding_node_from_binding(binding) for binding in bindings]
        if TypeChecker.is_list(target.type):
            new_target = Target(target.type.__args__[0], target.annotation)
            return [CollectionBindingNode(self._get_and_save_binding_nodes(new_target))]
        if TypeChecker.is_optional(target.type):
            new_target = Target(target.type.__args__[0], target.annotation)
            return self._get_binding_nodes(new_target)
        if TypeChecker.is_type(target.type):
            return self._get_binding_nodes_from_type(target)
        raise NoBindingFound(f"Could not find any bindings for {target}")

    def _get_binding_node_from_binding(self, binding: Binding[InjectedT]) -> SimpleBindingNode[Binding[InjectedT]]:
        binding_node = SimpleBindingNode(binding)
        if not isinstance(binding, ClassBinding):
            return binding_node
        if binding.scope not in self._scope_types:
            raise BindingError(f"{binding} has an unknown scope")

        self._current_class_binding = binding
        parameters = signature(binding.bound_type.__init__).parameters

        # Ignore 'self'
        for parameter in list(parameters.values())[1:]:
            # Ignore '*args' and '**kwargs'
            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                continue

            parameter_node = self._get_parameter_node(parameter)
            # pylint: disable=no-member
            if parameter.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
                binding_node.args.append(parameter_node)
            elif parameter.kind == Parameter.KEYWORD_ONLY:
                binding_node.kwargs.append(parameter_node)
        return binding_node

    def _get_parameter_node(self, parameter: Parameter) -> ParameterNode:
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_annotated(parameter.annotation):
                target = Target(parameter.annotation.original_type, parameter.annotation.annotation)
            else:
                target = Target(parameter.annotation, None)
            try:
                return ParameterNode(
                    parameter,
                    self._get_and_save_binding_nodes(target)[-1]
                )
            except NoBindingFound:
                pass
        if parameter.default is Parameter.empty:
            raise NonInjectableTypeError(f"Could not find binding or default value for {parameter.name}: "
                                         f"{parameter.annotation} required by {self._current_class_binding.bound_type}")
        return self._get_parameter_node_from_default(parameter)

    def _get_binding_nodes_from_type(self, target: Target[Type[InjectedT]]) -> List[BindingNode]:
        new_target = Target(target.type.__args__[0], target.annotation)
        cls_bindings = [
            binding
            for binding in self._binding_registry.get_bindings(new_target)
            if isinstance(binding, ClassBinding)
        ]
        if not cls_bindings:
            raise NoBindingFound(f"Could not find any binding for {target}")
        return [
            SimpleBindingNode(
                InstanceBinding(target.type, binding.bound_type, target.annotation),
            ) for binding in cls_bindings
        ]

    def _get_parameter_node_from_default(self, parameter: Parameter) -> ParameterNode:
        self.logger.debug(f"Could not find binding for {parameter.name}: {parameter.annotation} required by "
                          f"{self._current_class_binding.bound_type}, will use default value {parameter.default}")
        child_binding = InstanceBinding(parameter.annotation, parameter.default)
        child_binding_node = self._get_binding_node_from_binding(child_binding)
        return ParameterNode(
            parameter,
            child_binding_node,
        )
