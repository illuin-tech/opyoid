from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .provider_factory import ProviderFactory


class FromCacheProviderFactory(ProviderFactory):
    """Returns Providers for targets that are already in the registry."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return target in state.provider_registry

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        return state.provider_registry.get_provider(target)
