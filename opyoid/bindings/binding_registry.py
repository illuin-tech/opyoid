import logging
from typing import Any, cast, Dict, Optional, Type, TypeVar, Union

from opyoid.exceptions import NonInjectableTypeError
from opyoid.frozen_target import FrozenTarget
from opyoid.target import Target
from opyoid.utils import InjectedT
from .binding import Binding
from .class_binding import ClassBinding
from .instance_binding import InstanceBinding
from .multi_binding import MultiBinding
from .provider_binding import ProviderBinding
from .registered_binding import RegisteredBinding
from .registered_multi_binding import RegisteredMultiBinding
from .self_binding import SelfBinding

InjectedItemT = TypeVar("InjectedItemT", bound=Any)


class BindingRegistry:
    """Contains all bindings from a Module."""

    logger = logging.getLogger(__name__)

    def __init__(self, log_bindings: bool = False):
        self._bindings_by_target: Dict[FrozenTarget[Any], RegisteredBinding[Any]] = {}
        self._log_bindings = log_bindings

    def __contains__(self, item: Union[Target[Any], FrozenTarget[Any]]) -> bool:
        return self.get_binding(item) is not None

    def register(self, registered_binding: RegisteredBinding[Any], add_self_binding: bool = True) -> None:
        previous_binding = self._bindings_by_target.get(registered_binding.target)
        if self._should_append_to_multi_binding(registered_binding, previous_binding):
            previous_binding = cast(RegisteredMultiBinding[Any], previous_binding)
            self._append_to_multi_binding(cast(RegisteredMultiBinding[Any], registered_binding), previous_binding)
        else:
            self._create_or_override_binding(registered_binding, previous_binding)
        if add_self_binding:
            self._register_self_binding(registered_binding)

    @staticmethod
    def _should_append_to_multi_binding(
        new_binding: RegisteredBinding[InjectedItemT],
        previous_binding: Optional[RegisteredBinding[InjectedItemT]],
    ) -> bool:
        return (
            isinstance(new_binding, RegisteredMultiBinding)
            and previous_binding is not None
            and isinstance(previous_binding, RegisteredMultiBinding)
            and not cast(
                MultiBinding[InjectedItemT],
                new_binding.raw_binding,  # type: ignore[attr-defined]
            ).override_bindings
            and new_binding is not previous_binding
        )

    def _append_to_multi_binding(
        self,
        registered_binding: RegisteredMultiBinding[InjectedItemT],
        previous_binding: RegisteredMultiBinding[InjectedItemT],
    ) -> None:
        if self._log_bindings:
            self.logger.info(f"Adding {registered_binding.raw_binding} to previous binding")

        new_raw_binding = cast(MultiBinding[InjectedItemT], registered_binding.raw_binding)
        previous_raw_binding = cast(MultiBinding[InjectedItemT], previous_binding.raw_binding)
        for item_binding, raw_item_binding in zip(registered_binding.item_bindings, new_raw_binding.item_bindings):
            if item_binding not in previous_binding.item_bindings:
                previous_binding.item_bindings.append(item_binding)
                previous_raw_binding.item_bindings.append(raw_item_binding)

    def _create_or_override_binding(
        self, registered_binding: RegisteredBinding[InjectedT], previous_binding: Optional[RegisteredBinding[InjectedT]]
    ) -> None:
        if self._log_bindings:
            if previous_binding and previous_binding.raw_binding is not registered_binding.raw_binding:
                self.logger.info(f"Overriding {previous_binding.raw_binding!r} with {registered_binding.raw_binding!r}")
            elif not previous_binding:
                self.logger.debug(f"Registering {registered_binding.raw_binding!r}")
        self._bindings_by_target[registered_binding.target] = registered_binding

    def _register_self_binding(self, registered_binding: RegisteredBinding[Any]) -> None:
        binding = registered_binding.raw_binding
        self_binding: Optional[Binding[Any]] = None
        if isinstance(binding, ProviderBinding):
            if isinstance(binding.bound_provider, type):
                self_binding = SelfBinding(binding.bound_provider, scope=binding.scope, named=binding.named)
            else:
                self_binding = InstanceBinding(
                    type(binding.bound_provider),
                    binding.bound_provider,
                    named=binding.named,
                )
        elif isinstance(binding, ClassBinding):
            self_binding = SelfBinding(binding.bound_class, scope=binding.scope, named=binding.named)
        elif isinstance(binding, InstanceBinding) and not self._is_object_builtin(binding.bound_instance):
            self_binding = InstanceBinding(type(binding.bound_instance), binding.bound_instance, named=binding.named)
        elif isinstance(registered_binding, RegisteredMultiBinding):
            for item_binding in registered_binding.item_bindings:
                self._register_self_binding(item_binding)
        elif isinstance(binding, SelfBinding):
            self_binding = binding

        if self_binding is not None and self_binding.target not in self:
            self.register(
                RegisteredBinding(self_binding, registered_binding.binding_source, registered_binding.source_path)
            )

    def get_bindings_by_target(self) -> Dict[FrozenTarget[Any], RegisteredBinding[Any]]:
        return self._bindings_by_target

    def get_binding(
        self, target: Union[Target[InjectedT], FrozenTarget[InjectedT]]
    ) -> Optional[RegisteredBinding[InjectedT]]:
        if isinstance(target.type, str):
            possible_target_types = list(
                set(
                    cast(Type[InjectedT], available_target.type)
                    for available_target in self._bindings_by_target
                    if isinstance(available_target.type, type) and available_target.type.__name__ == target.type
                )
            )
            if len(possible_target_types) == 1:
                target.type = possible_target_types[0]
                frozen_target = FrozenTarget(target.type, target.named)
            elif possible_target_types:
                raise NonInjectableTypeError(
                    f"Could not find binding for '{target.type}': multiple types with this name found"
                )
            else:
                return None
        else:
            frozen_target = FrozenTarget(target.type, target.named)
        return self._bindings_by_target.get(frozen_target)

    @staticmethod
    def _is_object_builtin(target: Any) -> bool:
        return type(target) in [bool, bytearray, bytes, complex, float, int, str, type(None), dict, list, set, tuple]
