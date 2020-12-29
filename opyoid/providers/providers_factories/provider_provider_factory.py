from opyoid.bindings import FromInstanceProvider
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class ProviderProviderFactory(ProviderFactory):
    """Returns the provider for a provider target by transforming a Provider into a FromInstanceProvider."""

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return TypeChecker.is_provider(context.target.type)

    def create(self, context: InjectionContext[Provider[InjectedT]]) -> Provider[Provider[InjectedT]]:
        new_target = Target(context.target.type.__args__[0], context.target.named)
        new_context = context.get_child_context(new_target)
        return FromInstanceProvider(new_context.get_provider())
