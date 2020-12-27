from typing import Generic, TypeVar

from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .binding import Binding
from .registered_binding import RegisteredBinding

BindingT = TypeVar("BindingT", bound=Binding)


class BindingToProviderAdapter(Generic[BindingT]):
    """Creates a provider from a binding."""

    def accept(self, binding: Binding[InjectedT], context: InjectionContext[InjectedT]) -> bool:
        """Return True if this adapter can handle this binding."""
        raise NotImplementedError

    def create(self, binding: RegisteredBinding[BindingT], context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        """Returns a provider corresponding to this binding."""
        raise NotImplementedError
