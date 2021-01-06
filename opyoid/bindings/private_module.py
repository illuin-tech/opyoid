from typing import Set

from opyoid.frozen_target import FrozenTarget
from opyoid.utils import InjectedT
from .abstract_module import AbstractModule
from .registered_binding import RegisteredBinding


class PrivateModule(AbstractModule):
    def __init__(self):
        AbstractModule.__init__(self, log_bindings=True)
        self._exposed_bindings: Set[FrozenTarget] = set()

    def configure(self) -> None:
        raise NotImplementedError

    def is_exposed(self, target: FrozenTarget[InjectedT]) -> bool:
        return target in self._exposed_bindings

    def expose(self, *bindings: RegisteredBinding) -> None:
        for binding in bindings:
            self._exposed_bindings.add(binding.target)
