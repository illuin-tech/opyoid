from typing import Callable, Dict, List, Optional

from opyoid.provider import Provider
from opyoid.utils import InjectedT


class FromCallableProvider(Provider[InjectedT]):
    def __init__(
        self,
        injected_callable: Callable[..., InjectedT],
        positional_providers: List[Provider],
        args_provider: Optional[Provider[List]],
        keyword_providers: Dict[str, Provider],
    ) -> None:
        self._injected_callable = injected_callable
        self._positional_providers = positional_providers
        self._args_provider = args_provider
        self._keyword_providers = keyword_providers

    def get(self) -> InjectedT:
        args = [positional_provider.get() for positional_provider in self._positional_providers]
        if self._args_provider:
            args += self._args_provider.get()
        kwargs = {arg_name: keyword_provider.get() for arg_name, keyword_provider in self._keyword_providers.items()}
        return self._injected_callable(
            *args,
            **kwargs,
        )
