from typing import List, Optional, Type

from .bindings import Binding
from .bindings.abstract_binding_spec import AbstractBindingSpec
from .bindings.root_binding_spec import RootBindingSpec
from .injection_state import InjectionState
from .providers import ProviderCreator
from .target import Target
from .typings import InjectedT


class Injector:
    """Injection entry point.

    Registers all binding specs and bindings, then prepares all providers.
    """

    def __init__(self,
                 binding_specs: List[AbstractBindingSpec] = None,
                 bindings: List[Binding] = None) -> None:
        root_binding_spec = RootBindingSpec(self, binding_specs, bindings)
        root_binding_spec.configure_once()
        self._providers_creator = ProviderCreator()
        self._root_state = InjectionState(self._providers_creator, root_binding_spec.binding_registry)
        # Prepare providers
        for target in root_binding_spec.binding_registry.get_bindings_by_target():
            self._providers_creator.get_provider(target, self._root_state)

    def inject(self, target_type: Type[InjectedT], annotation: Optional[str] = None) -> InjectedT:
        return self._providers_creator.get_provider(Target(target_type, annotation), self._root_state).get()
