import logging

from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .from_registered_binding_provider_factory import FromRegisteredBindingProviderFactory
from .provider_factory import ProviderFactory


class FromBindingProviderFactory(ProviderFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._from_registered_binding_provider_factory = FromRegisteredBindingProviderFactory()

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        while not context.has_binding():
            if not context.injection_state.parent_state:
                return False
            context = context.get_new_state_context(context.injection_state.parent_state)
        return True

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if not context.has_binding():
            new_context = context.get_new_state_context(context.injection_state.parent_state)
            return new_context.get_provider()
        binding = context.get_binding()
        return self._from_registered_binding_provider_factory.create(binding, context)
