from typing import Generic, TypeVar

from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .binding import Binding

BindingT = TypeVar("BindingT", bound=Binding)


class BindingToProviderAdapter(Generic[BindingT]):
    """Creates a provider from a binding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        """Return True if this adapter can handle this binding."""
        raise NotImplementedError

    def create(self, binding: BindingT, state: InjectionState) -> Provider[InjectedT]:
        """Returns a provider corresponding to this binding."""
        raise NotImplementedError
