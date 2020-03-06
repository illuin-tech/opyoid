from typing import Dict, List

import attr

from illuin_inject.binding_registry import Target
from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class DependencyGraph:
    """Represents the dependency graph.

    Each binding is represented by a SimpleBindingNode.
    Each SimpleBindingNode contains ParameterNodes representing the parameters required to instantiate the bound class.
    Each ParameterNode contains the most recent BindingNode related to its type.
    This graph cannot have cycles, or an element would not be instantiable.
    Collections are represented by CollectionBindingNodes, that contain multiple BindingNodes.
    """
    binding_nodes_by_target: Dict[Target, List[BindingNode]] = attr.Factory(dict)
