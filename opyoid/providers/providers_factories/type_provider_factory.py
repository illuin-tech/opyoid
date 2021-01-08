from typing import Type

from opyoid.bindings import ClassBinding, FromInstanceProvider, SelfBinding
from opyoid.exceptions import NoBindingFound
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class TypeProviderFactory(ProviderFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_type(context.target.type)

    def create(self, context: InjectionContext[Type[InjectedT]]) -> Provider[Type[InjectedT]]:
        new_target = Target(context.target.type.__args__[0], context.target.named)
        new_context = context.get_child_context(new_target)
        binding = new_context.get_binding()
        if not binding or not isinstance(binding.raw_binding, (ClassBinding, SelfBinding)):
            raise NoBindingFound(f"Could not find any binding for {context.target!r}")
        if isinstance(binding.raw_binding, ClassBinding):
            return FromInstanceProvider(binding.raw_binding.bound_type)
        return FromInstanceProvider(binding.raw_binding.target_type)
