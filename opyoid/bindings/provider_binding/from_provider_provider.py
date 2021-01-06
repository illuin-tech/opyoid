from opyoid.provider import Provider
from opyoid.utils import InjectedT


class FromProviderProvider(Provider[InjectedT]):
    def __init__(self, provider_provider: Provider[Provider[InjectedT]]) -> None:
        self._provider_provider = provider_provider

    def get(self) -> InjectedT:
        provider: Provider[InjectedT] = self._provider_provider.get()
        return provider.get()
