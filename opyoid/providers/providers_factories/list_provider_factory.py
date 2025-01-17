from typing import Callable, cast, List

from opyoid.bindings import FromCallableProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory
from ...exceptions import IncompatibleProviderFactory


class ListProviderFactory(ProviderFactory):
    """Creates a Provider that groups the target list items providers."""

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if TypeChecker.is_pep585_list(context.target.type):
            new_target: Target[List[InjectedT]] = Target(
                List[context.target.type.__args__[0]],  # type: ignore[name-defined]
                context.target.named,
            )
            new_context = context.get_child_context(new_target)
            return FromCallableProvider(cast(Callable[..., InjectedT], list), [new_context.get_provider()], None, {})
        raise IncompatibleProviderFactory
