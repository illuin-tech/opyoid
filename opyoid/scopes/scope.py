from opyoid.provider import Provider
from opyoid.utils import InjectedT


class Scope:
    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        raise NotImplementedError
