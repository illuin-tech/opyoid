import logging
from typing import Dict, Optional

from illuin_inject.factory import Factory
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .class_binding import ClassBinding
from .factory_binding import FactoryBinding
from .multi_binding import MultiBinding
from .registered_binding import RegisteredBinding
from .self_binding import SelfBinding


class BindingRegistry:
    """Contains all bindings from a Module."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        self._bindings_by_target: Dict[Target[InjectedT], RegisteredBinding[InjectedT]] = {}

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return item in self._bindings_by_target

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
        if isinstance(binding, FactoryBinding):
            if isinstance(binding.bound_factory, type) \
                and issubclass(binding.bound_factory, Factory) \
                and Target(binding.bound_factory, binding.annotation) not in self:
                self_binding = SelfBinding(binding.bound_factory, scope=binding.scope, annotation=binding.annotation)
        elif isinstance(binding, ClassBinding):
            self_binding = SelfBinding(binding.bound_type, binding.scope, binding.annotation)

        if self_binding:
            self.register(RegisteredBinding(self_binding, registered_binding.source_path))

    def get_bindings_by_target(self) -> Dict[Target[InjectedT], RegisteredBinding[InjectedT]]:
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
                # noinspection PyTypeChecker
                target = Target(possible_target_types[0], target.annotation)
            elif possible_target_types:
                self.logger.error(f"Could not find binding for '{target.type}': multiple types with this name found")
        return self._bindings_by_target.get(target)
