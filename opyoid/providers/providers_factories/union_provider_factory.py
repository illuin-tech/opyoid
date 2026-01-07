from typing import cast, Union

from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory
from ...exceptions import IncompatibleProviderFactory, NoBindingFound


class UnionProviderFactory(ProviderFactory):
    """Returns the Provider for a Union type target."""

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if not TypeChecker.is_union(context.target.type):
            raise IncompatibleProviderFactory
        for subtype in cast(Union[InjectedT], context.target.type).__args__:
            try:
                new_target: Target[InjectedT] = Target(subtype, context.target.named)
                new_context = context.get_child_context(
                    new_target, current_class=context.current_class, current_parameter=context.current_parameter
                )
                return new_context.get_provider()
            except NoBindingFound:
                pass
        raise NoBindingFound(f"No binding found for {context.target}")
