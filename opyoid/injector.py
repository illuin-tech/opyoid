from typing import List, Optional, Type

from .bindings import Binding
from .bindings.abstract_module import AbstractModule
from .bindings.root_module import RootModule
from .injection_state import InjectionState
from .injector_options import InjectorOptions
from .providers import ProviderCreator
from .target import Target
from .typings import InjectedT


class Injector:
    """Injection entry point.

    Registers all modules and bindings, then prepares all providers.
    """

    def __init__(self,
                 modules: List[AbstractModule] = None,
                 bindings: List[Binding] = None,
                 options: InjectorOptions = None,
                 ) -> None:
        root_module = RootModule(self, modules, bindings)
        root_module.configure_once()
        self._provider_creator = ProviderCreator()
        self._root_state = InjectionState(
            self._provider_creator,
            root_module.binding_registry,
            options or InjectorOptions(),
        )
        # Prepare providers
        for target in root_module.binding_registry.get_bindings_by_target():
            self._provider_creator.get_provider(Target(target.type, target.annotation), self._root_state)

    def inject(self, target_type: Type[InjectedT], annotation: Optional[str] = None) -> InjectedT:
        return self._provider_creator.get_provider(Target(target_type, annotation), self._root_state).get()
