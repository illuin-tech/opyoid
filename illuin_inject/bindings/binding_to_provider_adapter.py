from typing import Generic, TYPE_CHECKING, TypeVar

from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .binding import Binding

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProviderCreator

BindingT = TypeVar("BindingT", bound=Binding)


class BindingToProviderAdapter(Generic[BindingT]):
    """Creates a provider from a binding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        """Return True if this adapter can handle this binding."""
        raise NotImplementedError

    def create(self, binding: BindingT, provider_creator: "ProviderCreator") -> Provider[InjectedT]:
        """Returns a provider corresponding to this binding."""
        raise NotImplementedError
