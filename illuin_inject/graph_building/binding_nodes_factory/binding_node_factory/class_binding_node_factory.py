from inspect import Parameter, signature
from typing import Container, List, TYPE_CHECKING, Type

from illuin_inject.bindings import Binding, ClassBinding
from illuin_inject.dependency_graph import BindingNode, ClassBindingNode, ParameterNode
from illuin_inject.exceptions import BindingError, NoBindingFound, NonInjectableTypeError
from illuin_inject.scopes import Scope
from illuin_inject.typings import InjectedT
from .binding_node_factory import BindingNodeFactory
from .parameter_node_factory import FromBindingsParameterNodeFactory, FromDefaultParameterNodeFactory, \
    ParameterNodeFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


# pylint: disable=no-self-use
class ClassBindingNodeFactory(BindingNodeFactory[ClassBinding]):
    """Creates a binding node from a ClassBinding."""

    def __init__(self, scope_types: Container[Type[Scope]]) -> None:
        self._scope_types = scope_types
        self._parameter_node_factories: List[ParameterNodeFactory] = [
            FromBindingsParameterNodeFactory(),
            FromDefaultParameterNodeFactory(),
        ]

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self, binding: ClassBinding[InjectedT], graph_builder: "GraphBuilder") -> BindingNode:
        if binding.scope not in self._scope_types:
            raise BindingError(f"{binding} has an unknown scope")

        parameters = signature(binding.bound_type.__init__).parameters
        args: List[ParameterNode] = []
        kwargs: List[ParameterNode] = []
        # Ignore 'self'
        for parameter in list(parameters.values())[1:]:
            # Ignore '*args' and '**kwargs'
            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                continue

            parameter_node = self._get_parameter_node(parameter, binding.bound_type, graph_builder)
            if parameter.kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]:
                args.append(parameter_node)
            elif parameter.kind == Parameter.KEYWORD_ONLY:
                kwargs.append(parameter_node)
        return ClassBindingNode(binding, args, kwargs)

    def _get_parameter_node(self,
                            parameter: Parameter,
                            current_class: Type,
                            graph_builder: "GraphBuilder") -> ParameterNode:
        for parameter_node_factory in self._parameter_node_factories:
            if parameter_node_factory.accept(parameter):
                try:
                    return parameter_node_factory.create(parameter, current_class, graph_builder)
                except NoBindingFound:
                    pass
        raise NonInjectableTypeError(f"Could not find binding or default value for {parameter.name}: "
                                     f"{parameter.annotation} required by {current_class}")
