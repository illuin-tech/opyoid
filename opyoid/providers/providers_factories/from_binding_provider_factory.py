import logging

from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .from_registered_binding_provider_factory import FromRegisteredBindingProviderFactory
from .provider_factory import ProviderFactory


class FromBindingProviderFactory(ProviderFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._from_registered_binding_provider_factory = FromRegisteredBindingProviderFactory()

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        while target not in state.binding_registry:
            if not state.parent_state:
                return False
            state = state.parent_state
        return True

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        if target not in state.binding_registry:
            return state.parent_state.provider_creator.get_provider(target, state.parent_state)
        binding = state.binding_registry.get_binding(target)
        return self._from_registered_binding_provider_factory.create(binding, state)
