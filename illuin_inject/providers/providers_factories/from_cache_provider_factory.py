from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .provider_factory import ProviderFactory


class FromCacheProviderFactory(ProviderFactory):
    """Returns Providers for targets that are already in the registry."""

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return target in state.provider_registry
        # while target not in state.provider_registry:
        #     if not state.parent_state:
        #         return False
        #     state = state.parent_state
        # return True

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        # while target not in state.provider_registry:
        #     state = state.parent_state
        return state.provider_registry.get_provider(target)
