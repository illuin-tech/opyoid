import logging
from typing import Dict, Optional

from opyoid.exceptions import NonInjectableTypeError
from opyoid.frozen_target import FrozenTarget
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .class_binding import ClassBinding
from .multi_binding import MultiBinding
from .provider_binding import ProviderBinding
from .registered_binding import RegisteredBinding
from .self_binding import SelfBinding


class BindingRegistry:
    """Contains all bindings from a Module."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        self._bindings_by_target: Dict[FrozenTarget[InjectedT], RegisteredBinding[InjectedT]] = {}

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return self.get_binding(item) is not None

    def register(self, registered_binding: RegisteredBinding) -> None:
        previous_binding = self._bindings_by_target.get(registered_binding.target)
        if isinstance(registered_binding.raw_binding, MultiBinding) \
            and previous_binding \
            and isinstance(previous_binding.raw_binding, MultiBinding) \
            and not registered_binding.raw_binding.override_bindings:
            self.logger.info(f"Adding {registered_binding.raw_binding} to {registered_binding.target}")
            previous_binding.raw_binding.item_bindings.extend(registered_binding.raw_binding.item_bindings)
            return
        if previous_binding:
            self.logger.info(f"Overriding {previous_binding.raw_binding!r} with {registered_binding.raw_binding!r}")
        self._bindings_by_target[registered_binding.target] = registered_binding
        self._register_self_binding(registered_binding)

    def _register_self_binding(self, registered_binding: RegisteredBinding) -> None:
        binding = registered_binding.raw_binding
        self_binding = None
        if isinstance(binding, ProviderBinding):
            if isinstance(binding.bound_provider, type) \
                and issubclass(binding.bound_provider, Provider) \
                and Target(binding.bound_provider, binding.annotation) not in self:
                self_binding = SelfBinding(binding.bound_provider, scope=binding.scope, annotation=binding.annotation)
        elif isinstance(binding, ClassBinding):
            self_binding = SelfBinding(binding.bound_type, binding.scope, binding.annotation)

        if self_binding:
            self.register(RegisteredBinding(self_binding, registered_binding.source_path))

    def get_bindings_by_target(self) -> Dict[FrozenTarget[InjectedT], RegisteredBinding[InjectedT]]:
        return self._bindings_by_target

    def get_binding(self, target: Target[InjectedT]) -> Optional[RegisteredBinding]:
        if isinstance(target.type, str):
            possible_target_types = list(set(
                available_target.type
                for available_target in self._bindings_by_target
                if isinstance(available_target.type, type)
                and available_target.type.__name__ == target.type
            ))
            if len(possible_target_types) == 1:
                target.type = possible_target_types[0]
            elif possible_target_types:
                raise NonInjectableTypeError(
                    f"Could not find binding for '{target.type}': multiple types with this name found")
        frozen_target = FrozenTarget(target.type, target.annotation)
        return self._bindings_by_target.get(frozen_target)
