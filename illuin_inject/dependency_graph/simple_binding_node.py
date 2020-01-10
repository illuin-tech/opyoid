from typing import Generic, List, TypeVar

import attr

from illuin_inject.bindings import Binding
from .binding_node import BindingNode
from .parameter_node import ParameterNode

BindingT = TypeVar("BindingT", bound=Binding)


@attr.s(auto_attribs=True)
class SimpleBindingNode(BindingNode, Generic[BindingT]):
    """Represents a binding in the dependency graph."""

    binding: BindingT
    args: List[ParameterNode] = attr.Factory(list)
    kwargs: List[ParameterNode] = attr.Factory(list)
