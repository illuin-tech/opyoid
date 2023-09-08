import logging
from typing import cast

from opyoid.exceptions import IncompatibleProviderFactory
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .from_registered_binding_provider_factory import FromRegisteredBindingProviderFactory
from .provider_factory import ProviderFactory
from ...bindings import RegisteredBinding


class FromBindingProviderFactory(ProviderFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._from_registered_binding_provider_factory = FromRegisteredBindingProviderFactory()

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        parent_context = context
        while not parent_context.has_binding():
            parent_state = parent_context.injection_state.parent_state
            if parent_state is None:
                raise IncompatibleProviderFactory
            parent_context = parent_context.get_new_state_context(parent_state)

        if not context.has_binding():
            new_context = context.get_new_state_context(cast(InjectionState, context.injection_state.parent_state))
            return new_context.get_provider()
        binding = cast(RegisteredBinding[InjectedT], context.get_binding())
        return self._from_registered_binding_provider_factory.create(binding, context)
