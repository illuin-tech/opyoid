from inspect import Parameter
from typing import TYPE_CHECKING, Type

from illuin_inject.dependency_graph import ParameterNode

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class ParameterNodeFactory:  # pragma: nocover
    def accept(self, parameter: Parameter) -> bool:
        raise NotImplementedError

    def create(self, parameter: Parameter, current_class: Type, graph_builder: "GraphBuilder") -> ParameterNode:
        raise NotImplementedError
