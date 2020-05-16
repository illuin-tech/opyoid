from typing import Generic
from uuid import UUID, uuid4

import attr

from illuin_inject.bindings import FactoryBinding
from illuin_inject.typings import InjectedT
from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class FactoryBindingNode(BindingNode, Generic[InjectedT]):
    """Represents a FactoryBinding in the dependency graph."""

    binding: FactoryBinding[InjectedT]
    factory_binding_node: BindingNode
    cache_key: UUID = attr.ib(factory=uuid4, repr=False, eq=False)
