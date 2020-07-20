from illuin_inject.factory import Factory
from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT


class FromFactoryProvider(Provider[InjectedT]):
    def __init__(self, factory_provider: Provider[Factory[InjectedT]]) -> None:
        self._factory_provider = factory_provider

    def get(self) -> InjectedT:
        return self._factory_provider.get().create()
