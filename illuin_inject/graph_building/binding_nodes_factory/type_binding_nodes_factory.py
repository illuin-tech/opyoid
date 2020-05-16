from typing import List, TYPE_CHECKING

from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import ClassBinding, InstanceBinding
from illuin_inject.dependency_graph import BindingNode, InstanceBindingNode
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .binding_nodes_factory import BindingNodesFactory

if TYPE_CHECKING:  # pragma: nocover
    from illuin_inject.graph_building.graph_builder import GraphBuilder


class TypeBindingNodesFactory(BindingNodesFactory):
    """Returns the binding nodes for a type target by transforming ClassBindings into InstanceBindings."""

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_type(target.type)

    def create(self, target: Target[InjectedT], graph_builder: "GraphBuilder") -> List[BindingNode]:
        new_target = Target(target.type.__args__[0], target.annotation)
        cls_bindings = [
            binding
            for binding in self._binding_registry.get_bindings(new_target)
            if isinstance(binding, ClassBinding)
        ]
        if not cls_bindings:
            raise NoBindingFound(f"Could not find any binding for {target}")
        return [
            InstanceBindingNode(
                InstanceBinding(target.type, binding.bound_type, target.annotation),
            ) for binding in cls_bindings
        ]
