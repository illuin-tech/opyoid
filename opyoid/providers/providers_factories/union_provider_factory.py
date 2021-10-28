from typing import Optional

from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory
from ...exceptions import NoBindingFound


class UnionProviderFactory(ProviderFactory):
    """Returns the Provider for an Union type target."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_union(context.target.type)

    def create(self, context: InjectionContext[Optional[InjectedT]]) -> Provider[InjectedT]:
        for subtype in context.target.type.__args__:
            try:
                new_target = Target(subtype, context.target.named)
                new_context = context.get_child_context(new_target)
                return new_context.get_provider()
            except NoBindingFound:
                pass
        raise NoBindingFound(f"No binding found for {context.target}")
