from typing import Any, Dict, Optional

from .exceptions import InjectException, NonInjectableTypeError
from .frozen_target import FrozenTarget
from .provider import Provider
from .target import Target
from .utils import InjectedT


class ProviderRegistry:
    """Stores Providers for each Target to create a cache."""

    def __init__(self) -> None:
        self._provider_by_target: Dict[FrozenTarget[Any], Provider[Any]] = {}

    def __contains__(self, item: Target[Any]) -> bool:
        return self.get_provider(item) is not None

    def set_provider(self, target: Target[InjectedT], provider: Provider[InjectedT]) -> None:
        if isinstance(target.type, str):
            raise InjectException()
        frozen_target = FrozenTarget(target.type, target.named)
        self._provider_by_target[frozen_target] = provider

    def get_provider(self, target: Target[InjectedT]) -> Optional[Provider[InjectedT]]:
        if isinstance(target.type, str):
            possible_target_types = list(
                set(
                    available_target.type
                    for available_target in self._provider_by_target
                    if isinstance(available_target.type, type) and available_target.type.__name__ == target.type
                )
            )
            if len(possible_target_types) == 1:
                # noinspection PyTypeChecker
                frozen_target = FrozenTarget(possible_target_types[0], target.named)
            elif possible_target_types:
                raise NonInjectableTypeError(
                    f"Could not find provider for '{target.type}': multiple types with this name found"
                )
            else:
                return None
        else:
            frozen_target = FrozenTarget(target.type, target.named)
        return self._provider_by_target.get(frozen_target)
