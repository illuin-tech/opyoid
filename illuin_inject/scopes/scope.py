from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT


class Scope:
    @classmethod
    def get_scoped_provider(cls, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        raise NotImplementedError
