from illuin_inject.bindings import FromInstanceProvider
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory


class ProviderProviderFactory(ProviderFactory):
    """Returns the provider for a provider target by transforming a Provider into a FromInstanceProvider."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return TypeChecker.is_provider(target.type)

    def create(self,
               target: Target[Provider[InjectedT]],
               state: InjectionState) -> Provider[Provider[InjectedT]]:
        new_target = Target(target.type.__args__[0], target.annotation)
        return FromInstanceProvider(state.provider_creator.get_provider(new_target, state))
