import logging
from typing import Dict, List, Type, Union

from .bindings import Binding
from .typings import InjectedT


class BindingRegistry:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._bindings_by_target_type: Dict[Type[InjectedT], List[Binding[InjectedT]]] = {}

    def register(self, binding: Binding) -> None:
        if binding.target_type not in self._bindings_by_target_type:
            self._bindings_by_target_type[binding.target_type] = []
        self._bindings_by_target_type[binding.target_type].append(binding)

    def update(self, binding_registry: "BindingRegistry") -> None:
        for bindings in binding_registry.get_bindings_by_target_type().values():
            for binding in bindings:
                self.register(binding)

    def get_bindings_by_target_type(self) -> Dict[Type[InjectedT], List[Binding[InjectedT]]]:
        return self._bindings_by_target_type

    def get_bindings(self, target_type: Union[Type[InjectedT], str]) -> List[Binding]:
        if isinstance(target_type, str):
            possible_target_types = [
                available_target_type
                for available_target_type in self._bindings_by_target_type
                if available_target_type.__name__ == target_type
            ]
            if len(possible_target_types) == 1:
                target_type = possible_target_types[0]
            elif possible_target_types:
                self.logger.error(f"Could not find binding for '{target_type}': multiple types with this name found")
        return self._bindings_by_target_type.get(target_type, [])
