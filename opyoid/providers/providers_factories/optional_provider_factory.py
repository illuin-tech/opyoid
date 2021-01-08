from typing import Optional

from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class OptionalProviderFactory(ProviderFactory):
    """Returns the Provider for an optional type target."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_optional(context.target.type)

    def create(self, context: InjectionContext[Optional[InjectedT]]) -> Provider[InjectedT]:
        new_target = Target(context.target.type.__args__[0], context.target.named)
        new_context = context.get_child_context(new_target)
        return new_context.get_provider()
