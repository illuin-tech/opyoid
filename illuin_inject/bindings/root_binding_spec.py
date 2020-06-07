from typing import List, Optional, TYPE_CHECKING

from illuin_inject.scopes import ImmediateScope, PerLookupScope, SingletonScope, ThreadScope
from .abstract_binding_spec import AbstractBindingSpec
from .binding import Binding
from .binding_spec import BindingSpec

if TYPE_CHECKING:
    from illuin_inject.injector import Injector


class RootBindingSpec(BindingSpec):
    def __init__(self,
                 injector: "Injector",
                 binding_specs: Optional[List[AbstractBindingSpec]],
                 bindings: Optional[List[Binding]]) -> None:
        BindingSpec.__init__(self)
        self._injector = injector
        self._binding_specs = binding_specs or []
        self._bindings = bindings or []

    def configure(self) -> None:
        # pylint: disable=import-outside-toplevel
        from illuin_inject.injector import Injector

        self.bind(Injector, to_instance=self._injector)
        self.bind(ImmediateScope, to_instance=ImmediateScope())
        self.bind(PerLookupScope, to_instance=PerLookupScope())
        self.bind(SingletonScope, to_instance=SingletonScope())
        self.bind(ThreadScope, to_instance=ThreadScope())
        for binding_spec in self._binding_specs:
            self.install(binding_spec)
        for binding in self._bindings:
            self._register(binding)
