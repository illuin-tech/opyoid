from typing import Dict, List, Optional, Type

from opyoid.provider import Provider
from opyoid.utils import InjectedT


class FromClassProvider(Provider[InjectedT]):
    def __init__(self,
                 injected_type: Type[InjectedT],
                 positional_providers: List[Provider],
                 args_provider: Optional[Provider[List]],
                 keyword_providers: Dict[str, Provider]) -> None:
        self._injected_type = injected_type
        self._positional_providers = positional_providers
        self._args_provider = args_provider
        self._keyword_providers = keyword_providers

    def get(self) -> InjectedT:
        args = [
            positional_provider.get()
            for positional_provider in self._positional_providers
        ]
        if self._args_provider:
            args += self._args_provider.get()
        kwargs = {
            arg_name: keyword_provider.get()
            for arg_name, keyword_provider in self._keyword_providers.items()
        }
        return self._injected_type(
            *args,
            **kwargs,
        )
