from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT


class ProviderFactory:
    """Creates a provider for each target.

    A target corresponds to either a Binding target or a dependency of a Binding target.
    """

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        """Returns True if this factory can handle this target."""
        raise NotImplementedError

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        """Returns the provider corresponding to this target."""
        raise NotImplementedError
