import logging
from typing import cast, Type

from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .callable_to_provider_adapter import CallableToProviderAdapter
from .self_binding import SelfBinding


class SelfBindingToProviderAdapter(BindingToProviderAdapter):
    """Creates a Provider from a SelfBinding."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        BindingToProviderAdapter.__init__(self)
        self._adapter = CallableToProviderAdapter()

    def create(
        self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        if isinstance(binding.raw_binding, SelfBinding):
            target_class = cast(Type[InjectedT], binding.target.type)
            context.current_class = target_class
            return self._adapter.create(target_class, context, binding.raw_binding.scope)
        raise IncompatibleAdapter
