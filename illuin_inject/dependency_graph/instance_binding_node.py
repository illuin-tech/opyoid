from typing import Generic

import attr

from illuin_inject.bindings import InstanceBinding
from illuin_inject.typings import InjectedT
from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class InstanceBindingNode(BindingNode, Generic[InjectedT]):
    """Represents an InstanceBinding in the dependency graph."""

    binding: InstanceBinding[InjectedT]
