from typing import Type

from opyoid.bindings import ClassBinding, FromInstanceProvider, SelfBinding
from opyoid.exceptions import NoBindingFound
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.typings import InjectedT
from .provider_factory import ProviderFactory


class TypeProviderFactory(ProviderFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_type(target.type)

    def create(self,
               target: Target[Type[InjectedT]],
               state: InjectionState) -> Provider[Type[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        binding = state.binding_registry.get_binding(new_target)
        if not binding or not isinstance(binding.raw_binding, (ClassBinding, SelfBinding)):
            raise NoBindingFound(f"Could not find any binding for {target}")
        if isinstance(binding.raw_binding, ClassBinding):
            return FromInstanceProvider(binding.raw_binding.bound_type)
        return FromInstanceProvider(binding.raw_binding.target_type)
