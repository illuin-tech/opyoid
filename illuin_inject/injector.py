from typing import List, Optional, Type

from .scopes import ImmediateScope, PerLookupScope, SingletonScope, ThreadScope
from .bindings import Binding, BindingRegistry, BindingSpec, InstanceBinding
from .providers import ProviderCreator
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
        self._add_default_bindings()
        for binding_spec in binding_specs or []:
            binding_spec.configure()
            self._binding_registry.update(binding_spec.binding_registry)
        for binding in bindings or []:
            self._binding_registry.register(binding)
        self._providers_creator = ProviderCreator(self._binding_registry)
        # Prepare providers
        for target in self._binding_registry.get_bindings_by_target():
            self._providers_creator.get_provider(target)

    def inject(self, target_type: Type[InjectedT], annotation: Optional[str] = None) -> InjectedT:
        return self._providers_creator.get_provider(Target(target_type, annotation)).get()

    def _add_default_bindings(self):
        self._binding_registry.register(InstanceBinding(self.__class__, self))
        self._binding_registry.register(InstanceBinding(ImmediateScope, ImmediateScope()))
        self._binding_registry.register(InstanceBinding(PerLookupScope, PerLookupScope()))
        self._binding_registry.register(InstanceBinding(SingletonScope, SingletonScope()))
        self._binding_registry.register(InstanceBinding(ThreadScope, ThreadScope()))
