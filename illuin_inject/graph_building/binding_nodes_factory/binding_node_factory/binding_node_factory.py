from typing import Generic, TYPE_CHECKING, TypeVar

from illuin_inject.bindings import Binding
from illuin_inject.dependency_graph import BindingNode
from illuin_inject.typings import InjectedT

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder

BindingT = TypeVar("BindingT", bound=Binding)


class BindingNodeFactory(Generic[BindingT]):  # pragma: nocover
    """Creates a binding node from a binding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        """Return True if this factory can handle this binding."""
        raise NotImplementedError

    def create(self, binding: BindingT, graph_builder: "GraphBuilder") -> BindingNode:
        """Returns a binding node corresponding to this binding."""
        raise NotImplementedError
