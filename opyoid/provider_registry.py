from typing import Dict

from .exceptions import NonInjectableTypeError
from .frozen_target import FrozenTarget
from .provider import Provider
from .target import Target
from .utils import InjectedT


class ProviderRegistry:
    """Stores Providers for each Target to create a cache."""

    def __init__(self):
        self._provider_by_target: Dict[FrozenTarget, Provider] = {}

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return self.get_provider(item) is not None

    def set_provider(self, target: Target[InjectedT], provider: Provider[InjectedT]) -> None:
        frozen_target = FrozenTarget(target.type, target.named)
        self._provider_by_target[frozen_target] = provider

    def get_provider(self, target: Target[InjectedT]) -> Provider[InjectedT]:
        frozen_target = FrozenTarget(target.type, target.named)
        if isinstance(target.type, str):
            possible_target_types = list(set(
                available_target.type
                for available_target in self._provider_by_target
                if isinstance(available_target.type, type)
                and available_target.type.__name__ == target.type
            ))
            if len(possible_target_types) == 1:
                # noinspection PyTypeChecker
                frozen_target = FrozenTarget(possible_target_types[0], target.named)
            elif possible_target_types:
                raise NonInjectableTypeError(
                    f"Could not find provider for '{target.type}': multiple types with this name found")
        return self._provider_by_target.get(frozen_target)
