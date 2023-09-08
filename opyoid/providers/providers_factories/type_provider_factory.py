from typing import Any, cast, Type

from opyoid.bindings import ClassBinding, FromInstanceProvider, SelfBinding
from opyoid.exceptions import IncompatibleProviderFactory, NoBindingFound
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class TypeProviderFactory(ProviderFactory):
    """Returns the provider for a type target by transforming ClassBindings into a FromInstanceProvider."""

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if not TypeChecker.is_type(context.target.type):
            raise IncompatibleProviderFactory
        new_target: Target[Type[Any]] = Target(
            context.target.type.__args__[0], context.target.named  # type: ignore[union-attr]
        )
        new_context = context.get_child_context(new_target)
        binding = new_context.get_binding()
        if not binding or not isinstance(binding.raw_binding, (ClassBinding, SelfBinding)):
            raise NoBindingFound(f"Could not find any binding for {context.target!r}")
        if isinstance(binding.raw_binding, ClassBinding):
            return FromInstanceProvider(cast(InjectedT, binding.raw_binding.bound_class))
        return FromInstanceProvider(cast(InjectedT, binding.raw_binding.target_type))
