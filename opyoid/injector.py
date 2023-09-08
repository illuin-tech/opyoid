from typing import Any, List, Optional, Type, TypeVar, Union

from .bindings import Binding
from .bindings.abstract_module import AbstractModule
from .bindings.root_module import RootModule
from .injection_context import InjectionContext
from .injection_state import InjectionState
from .injector_options import InjectorOptions
from .providers import ProviderCreator
from .target import Target
from .utils import InjectedT


class Injector:
    """Injection entry point.

    Registers all modules and bindings, then prepares all providers.
    """

    def __init__(
        self,
        modules: Optional[List[Union[AbstractModule, Type[AbstractModule]]]] = None,
        bindings: Optional[List[Binding[Any]]] = None,
        options: Optional[InjectorOptions] = None,
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
            injection_context: InjectionContext[Any] = InjectionContext(
                Target(target.type, target.named), self._root_state
            )
            injection_context.get_provider()

    def inject(self, target_type: Union[Type[InjectedT], TypeVar, Any], *, named: Optional[str] = None) -> InjectedT:
        injection_context: InjectionContext[InjectedT] = InjectionContext(Target(target_type, named), self._root_state)
        return injection_context.get_provider().get()
