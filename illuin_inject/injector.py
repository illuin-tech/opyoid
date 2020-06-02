from typing import List, Optional, Type

from .bindings import Binding, BindingRegistry, BindingSpec, InstanceBinding
from .providers import ProvidersCreator
from .target import Target
from .typings import InjectedT


class Injector:
    """Injection entry point.

    Registers all binding specs and bindings, then prepares all providers.
    """

    def __init__(self,
                 binding_specs: List[BindingSpec] = None,
                 bindings: List[Binding] = None,
                 binding_registry: BindingRegistry = None) -> None:
        self._binding_registry: BindingRegistry = binding_registry or BindingRegistry()
        self._binding_registry.register(InstanceBinding(self.__class__, self))
        for binding_spec in binding_specs or []:
            binding_spec.configure()
            self._binding_registry.update(binding_spec.binding_registry)
        for binding in bindings or []:
            self._binding_registry.register(binding)
        self._providers_creator = ProvidersCreator(self._binding_registry)
        # Prepare providers
        for target in self._binding_registry.get_bindings_by_target():
            self._providers_creator.get_providers(target)

    def inject(self, target_type: Type[InjectedT], annotation: Optional[str] = None) -> InjectedT:
        return self._providers_creator.get_providers(Target(target_type, annotation))[-1].get()
