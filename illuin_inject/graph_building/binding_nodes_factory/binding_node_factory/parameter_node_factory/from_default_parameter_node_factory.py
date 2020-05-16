import logging
from inspect import Parameter
from typing import TYPE_CHECKING, Type

from illuin_inject.bindings import InstanceBinding
from illuin_inject.dependency_graph import InstanceBindingNode, ParameterNode
from .parameter_node_factory import ParameterNodeFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class FromDefaultParameterNodeFactory(ParameterNodeFactory):
    """Creates a Parameter Node by using the parameter default value."""

    logger = logging.getLogger(__name__)

    def accept(self, parameter: Parameter) -> bool:
        return parameter.default is not Parameter.empty

    def create(self, parameter: Parameter, current_class: Type, graph_builder: "GraphBuilder") -> ParameterNode:
        self.logger.debug(f"Could not find binding for {parameter.name}: {parameter.annotation} required by "
                          f"{current_class}, will use default value {parameter.default}")
        child_binding = InstanceBinding(parameter.annotation, parameter.default)
        child_binding_node = InstanceBindingNode(child_binding)
        return ParameterNode(
            parameter,
            child_binding_node,
        )
