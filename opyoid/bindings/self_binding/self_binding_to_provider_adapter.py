import logging

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .callable_to_provider_adapter import CallableToProviderAdapter
from .self_binding import SelfBinding


class SelfBindingToProviderAdapter(BindingToProviderAdapter[SelfBinding]):
    """Creates a Provider from a SelfBinding."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        BindingToProviderAdapter.__init__(self)
        self._adapter = CallableToProviderAdapter()

    def accept(self, binding: Binding[InjectedT], context: InjectionContext) -> bool:
        return isinstance(binding, SelfBinding)

    def create(
        self, binding: RegisteredBinding[SelfBinding[InjectedT]], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        return self._adapter.create(binding, binding.target.type, context)
