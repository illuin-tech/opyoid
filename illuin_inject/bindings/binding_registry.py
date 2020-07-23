import logging
from typing import Dict, Optional

from illuin_inject.factory import Factory
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding import Binding
from .class_binding import ClassBinding
from .factory_binding import FactoryBinding
from .multi_binding import MultiBinding


class BindingRegistry:
    """Contains all bindings."""

    logger = logging.getLogger(__name__)

    def __init__(self):
        self._bindings_by_target: Dict[Target[InjectedT], Binding[InjectedT]] = {}

    def __contains__(self, item: Target[InjectedT]) -> bool:
        return item in self._bindings_by_target

    def register(self, binding: Binding) -> None:
        previous_binding = self._bindings_by_target.get(binding.target)
        if isinstance(binding, MultiBinding) \
            and previous_binding \
            and isinstance(previous_binding, MultiBinding) \
            and not binding.override_bindings:
            self.logger.info(f"Adding {binding} to {binding.target_type}:{binding.annotation}")
            previous_binding.item_bindings.extend(binding.item_bindings)
            return
        if binding.target in self._bindings_by_target:
            self.logger.info(f"Overriding {self._bindings_by_target[binding.target]} with {binding!r}")
        self._bindings_by_target[binding.target] = binding
        if isinstance(binding, FactoryBinding):
            self._register_factory(binding)

    def _register_factory(self, binding: FactoryBinding) -> None:
        if isinstance(binding.bound_factory, type) and issubclass(binding.bound_factory, Factory):
            self.register(
                ClassBinding(binding.bound_factory, scope=binding.scope, annotation=binding.annotation)
            )

    def get_bindings_by_target(self) -> Dict[Target[InjectedT], Binding[InjectedT]]:
        return self._bindings_by_target

    def update(self, binding_registry: "BindingRegistry") -> None:
        for binding in binding_registry.get_bindings_by_target().values():
            self.register(binding)

    def get_binding(self, target: Target[InjectedT]) -> Optional[Binding]:
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
