from inspect import Parameter
from typing import TYPE_CHECKING, Type

from illuin_inject.dependency_graph import ParameterNode
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from .parameter_node_factory import ParameterNodeFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class FromBindingsParameterNodeFactory(ParameterNodeFactory):
    """Creates a Parameter Node by using the parameter annotation."""

    def accept(self, parameter: Parameter) -> bool:
        return parameter.annotation is not Parameter.empty

    def create(self, parameter: Parameter, current_class: Type, graph_builder: "GraphBuilder") -> ParameterNode:
        if TypeChecker.is_annotated(parameter.annotation):
            target = Target(parameter.annotation.original_type, parameter.annotation.annotation)
        else:
            target = Target(parameter.annotation, None)
        return ParameterNode(
            parameter,
            graph_builder.get_and_save_binding_nodes(target)[-1]
        )
