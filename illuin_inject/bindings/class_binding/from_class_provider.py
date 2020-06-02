from typing import Dict, List, Type

from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT


class FromClassProvider(Provider[InjectedT]):
    def __init__(self,
                 injected_type: Type[InjectedT],
                 args_providers: List[Provider],
                 kwargs_providers: Dict[str, Provider]) -> None:
        self._injected_type = injected_type
        self._args_providers = args_providers
        self._kwargs_providers = kwargs_providers

    def get(self) -> InjectedT:
        args = [
            arg_provider.get()
            for arg_provider in self._args_providers
        ]
        kwargs = {
            arg_name: kwarg_provider.get()
            for arg_name, kwarg_provider in self._kwargs_providers.items()
        }
        return self._injected_type(
            *args,
            **kwargs,
        )
