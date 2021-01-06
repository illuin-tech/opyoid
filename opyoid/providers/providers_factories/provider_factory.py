from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT


class ProviderFactory:
    """Creates a provider for each target.

    A target corresponds to either a Binding target or a dependency of a Binding target.
    """

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        """Returns True if this factory can handle this target."""
        raise NotImplementedError

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        """Returns the provider corresponding to this target."""
        raise NotImplementedError
