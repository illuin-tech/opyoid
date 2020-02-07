import inspect

import attr

from .binding_node import BindingNode


@attr.s(auto_attribs=True)
class ParameterNode:
    parameter: inspect.Parameter
    binding_node: BindingNode
