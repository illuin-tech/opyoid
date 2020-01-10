from typing import Dict, List, Type

import attr

from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class DependencyGraph:
    """Represents the dependency graph.

    Each binding is represented by a SimpleBindingNode.
    Each SimpleBindingNode contains ParameterNodes representing the parameters required to instantiate the bound class.
    Each ParameterNode contains the most recent BindingNode related to its type.
    This graph cannot have cycles, or an element would not be instantiable.
    Lists are represented by MultiBindingNodes, that contain multiple BindingNodes.
    """
    binding_nodes_by_type: Dict[Type, List[BindingNode]] = attr.Factory(dict)
