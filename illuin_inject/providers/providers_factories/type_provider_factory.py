from typing import TYPE_CHECKING, Type

from illuin_inject.bindings import BindingRegistry, ClassBinding, FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory

if TYPE_CHECKING:
    from illuin_inject.providers import ProviderCreator


class TypeProviderFactory(ProviderFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def __init__(self, binding_registry: BindingRegistry) -> None:
        self._binding_registry = binding_registry

    def accept(self, target: Target[InjectedT]) -> bool:
        return TypeChecker.is_type(target.type)

    def create(self,
               target: Target[Type[InjectedT]],
               provider_creator: "ProviderCreator") -> Provider[Type[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        binding = self._binding_registry.get_binding(new_target)
        if not isinstance(binding, ClassBinding):
            raise NoBindingFound(f"Could not find any binding for {target}")
        return FromInstanceProvider(binding.bound_type)
