from typing import Generic, List
from uuid import UUID, uuid4

import attr

from illuin_inject.bindings import ClassBinding
from illuin_inject.typings import InjectedT
from .binding_node import BindingNode
from .parameter_node import ParameterNode


@attr.s(auto_attribs=True)
class ClassBindingNode(BindingNode, Generic[InjectedT]):
    """Represents a ClassBinding in the dependency graph."""

    binding: ClassBinding[InjectedT]
    args: List[ParameterNode] = attr.Factory(list)
    kwargs: List[ParameterNode] = attr.Factory(list)
    cache_key: UUID = attr.ib(factory=uuid4, repr=False, eq=False)
