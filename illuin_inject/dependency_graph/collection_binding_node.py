from typing import Callable, Collection, Iterable, List

import attr

from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class CollectionBindingNode(BindingNode):
    """Represents bindings to a collection items in the dependency graph.
    """
    sub_bindings: List[BindingNode]
    collection_constructor: Callable[[Iterable], Collection]
