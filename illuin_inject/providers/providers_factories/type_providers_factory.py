from typing import List, TYPE_CHECKING, Type

from illuin_inject.bindings import BindingRegistry, ClassBinding, FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .providers_factory import ProvidersFactory

if TYPE_CHECKING:
    from illuin_inject.providers import ProvidersCreator


class TypeProvidersFactory(ProvidersFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_type(target.type)

    def create(self,
               target: Target[Type[InjectedT]],
               providers_creator: "ProvidersCreator") -> List[Provider[Type[InjectedT]]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        cls_bindings = [
            binding
            for binding in self._binding_registry.get_bindings(new_target)
            if isinstance(binding, ClassBinding)
        ]
        if not cls_bindings:
            raise NoBindingFound(f"Could not find any binding for {target}")
        return [
            FromInstanceProvider(binding.bound_type)
            for binding in cls_bindings
        ]
