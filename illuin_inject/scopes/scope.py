from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT


class Scope:
    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        raise NotImplementedError
