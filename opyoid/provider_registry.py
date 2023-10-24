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
        frozen_target = self._get_frozen_target(target)
        if not frozen_target:
            raise InjectException()
        self._provider_by_target[frozen_target] = provider

    def get_provider(self, target: Target[InjectedT]) -> Optional[Provider[InjectedT]]:
        frozen_target = self._get_frozen_target(target)
        if not frozen_target:
            return None
        return self._provider_by_target.get(frozen_target)

    def _get_frozen_target(self, target: Target[InjectedT]) -> Optional[FrozenTarget[InjectedT]]:
        if not isinstance(target.type, str):
            return FrozenTarget(target.type, target.named)

        possible_target_types = list(
            set(
                available_target.type
                for available_target in self._provider_by_target
                if isinstance(available_target.type, type) and available_target.type.__name__ == target.type
            )
        )
        if len(possible_target_types) == 1:
            # noinspection PyTypeChecker
            return FrozenTarget(possible_target_types[0], target.named)
        if possible_target_types:
            raise NonInjectableTypeError(
                f"Could not find provider for '{target.type}': multiple types with this name found"
            )
        return None
