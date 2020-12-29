import logging
from typing import Dict, Optional, cast

from opyoid.exceptions import NonInjectableTypeError
from opyoid.frozen_target import FrozenTarget
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
from .class_binding import ClassBinding
from .instance_binding import InstanceBinding
from .provider_binding import ProviderBinding
from .registered_binding import RegisteredBinding
from .registered_multi_binding import RegisteredMultiBinding
from .self_binding import SelfBinding


class BindingRegistry:
    """Contains all bindings from a Module."""

    logger = logging.getLogger(__name__)

    def __init__(self, log_bindings: bool = False):
        self._bindings_by_target: Dict[FrozenTarget[InjectedT], RegisteredBinding[InjectedT]] = {}
        self._log_bindings = log_bindings

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return self.get_binding(item) is not None

    def register(self, registered_binding: RegisteredBinding, add_self_binding: bool = True) -> None:
        previous_binding = self._bindings_by_target.get(registered_binding.target)
        if isinstance(registered_binding, RegisteredMultiBinding) \
            and previous_binding \
            and isinstance(previous_binding, RegisteredMultiBinding) \
            and not cast(RegisteredMultiBinding, registered_binding).raw_binding.override_bindings:
            if self._log_bindings:
                self.logger.info(f"Adding {registered_binding.raw_binding} to previous binding")
            previous_binding.item_bindings.extend(registered_binding.item_bindings)
            return
        if self._log_bindings:
            if previous_binding and previous_binding.raw_binding != registered_binding.raw_binding:
                self.logger.info(f"Overriding {previous_binding.raw_binding!r} with {registered_binding.raw_binding!r}")
            elif not previous_binding:
                self.logger.debug(f"Registering {registered_binding.raw_binding!r}")
        self._bindings_by_target[registered_binding.target] = registered_binding
        if add_self_binding:
            self._register_self_binding(registered_binding)

    def _register_self_binding(self, registered_binding: RegisteredBinding) -> None:
        binding = registered_binding.raw_binding
        self_binding = None
        if isinstance(binding, ProviderBinding):
            if isinstance(binding.bound_provider, Provider):
                self_binding = InstanceBinding(type(binding.bound_provider), binding.bound_provider, binding.named)
            else:
                self_binding = SelfBinding(binding.bound_provider, scope=binding.scope, named=binding.named)
        elif isinstance(binding, ClassBinding):
            self_binding = SelfBinding(binding.bound_type, binding.scope, binding.named)
        elif isinstance(binding, InstanceBinding):
            self_binding = InstanceBinding(type(binding.bound_instance), binding.bound_instance, binding.named)
        elif isinstance(registered_binding, RegisteredMultiBinding):
            for item_binding in registered_binding.item_bindings:
                self._register_self_binding(item_binding)

        if self_binding and self_binding.target not in self:
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
        frozen_target = FrozenTarget(target.type, target.named)
        return self._bindings_by_target.get(frozen_target)
