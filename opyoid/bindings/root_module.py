from typing import List, Optional, TYPE_CHECKING

from opyoid.scopes import ImmediateScope, PerLookupScope, SingletonScope, ThreadScope
from .abstract_module import AbstractModule
from .binding import Binding
from .module import Module

if TYPE_CHECKING:
    from opyoid.injector import Injector


class RootModule(Module):
    def __init__(self,
                 injector: "Injector",
                 modules: Optional[List[AbstractModule]],
                 bindings: Optional[List[Binding]]) -> None:
        Module.__init__(self, log_bindings=True)
        self._injector = injector
        self._modules = modules or []
        self._bindings = bindings or []

    def configure(self) -> None:
        # pylint: disable=import-outside-toplevel
        from opyoid.injector import Injector

        self.bind(Injector, to_instance=self._injector)
        self.bind(ImmediateScope, to_instance=ImmediateScope())
        self.bind(PerLookupScope, to_instance=PerLookupScope())
        self.bind(SingletonScope, to_instance=SingletonScope())
        self.bind(ThreadScope, to_instance=ThreadScope())
        for module in self._modules:
            self.install(module)
        for binding in self._bindings:
            self._register(binding)
