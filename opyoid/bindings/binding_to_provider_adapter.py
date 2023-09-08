from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .registered_binding import RegisteredBinding


class BindingToProviderAdapter:
    """Creates a provider from a binding."""

    def create(
        self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        """Returns a provider corresponding to this binding or raises IncompatibleAdapter."""
        raise NotImplementedError
