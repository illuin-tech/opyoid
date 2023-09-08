from typing import Any, Set

from opyoid.frozen_target import FrozenTarget
from .abstract_module import AbstractModule
from .registered_binding import RegisteredBinding


class PrivateModule(AbstractModule):
    def __init__(self) -> None:
        AbstractModule.__init__(self, log_bindings=True)
        self._exposed_bindings: Set[FrozenTarget[Any]] = set()

    def configure(self) -> None:
        raise NotImplementedError

    def is_exposed(self, target: FrozenTarget[Any]) -> bool:
        return target in self._exposed_bindings

    def expose(self, *bindings: RegisteredBinding[Any]) -> None:
        for binding in bindings:
            self._exposed_bindings.add(binding.target)
