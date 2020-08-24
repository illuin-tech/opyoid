import logging
from typing import List

from opyoid.bindings import Binding, BindingToProviderAdapter, ClassBindingToProviderAdapter, \
    InstanceBindingToProviderAdapter, MultiBindingToProviderAdapter, ProviderBindingToProviderAdapter, \
    SelfBindingToProviderAdapter
from opyoid.exceptions import BindingError
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .provider_factory import ProviderFactory


class FromBindingProviderFactory(ProviderFactory):
    """Creates Providers, one per binding."""

    logger = logging.getLogger(__name__)

    def __init__(self) -> None:
        self._binding_to_provider_adapters: List[BindingToProviderAdapter] = [
            SelfBindingToProviderAdapter(),
            InstanceBindingToProviderAdapter(),
            ClassBindingToProviderAdapter(),
            ProviderBindingToProviderAdapter(),
            MultiBindingToProviderAdapter(self),
        ]

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        while target not in state.binding_registry:
            if not state.parent_state:
                return False
            state = state.parent_state
        return True

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        while target not in state.binding_registry:
            return state.parent_state.provider_creator.get_provider(target, state.parent_state)
        binding = state.binding_registry.get_binding(target)
        module_path = binding.source_path
        if not module_path:
            return self.create_from_binding(binding.raw_binding, state)
        if module_path[0] not in state.state_by_module:
            state.state_by_module[module_path[0]] = InjectionState(
                state.provider_creator,
                module_path[0].binding_registry,
                state.options,
                state,
            )
        return state.provider_creator.get_provider(target, state.state_by_module[module_path[0]])

    def create_from_binding(self,
                            binding: Binding[InjectedT],
                            state: InjectionState) -> Provider[InjectedT]:
        for adapter in self._binding_to_provider_adapters:
            if adapter.accept(binding, state):
                return adapter.create(binding, state)
        raise BindingError(f"Could not find a BindingToProviderAdapter for {binding!r}")
