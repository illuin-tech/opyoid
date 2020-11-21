import logging
from typing import List

from opyoid.bindings import Binding, BindingToProviderAdapter, ClassBindingToProviderAdapter, \
    InstanceBindingToProviderAdapter, MultiBindingToProviderAdapter, ProviderBindingToProviderAdapter, \
    SelfBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import BindingError
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT


class FromRegisteredBindingProviderFactory:
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

    def create(self,
               binding: RegisteredBinding[Binding[InjectedT]],
               state: InjectionState,
               cache_provider: bool = True) -> Provider[InjectedT]:
        module_path = binding.source_path
        while module_path:
            if module_path[0] not in state.state_by_module:
                state.state_by_module[module_path[0]] = InjectionState(
                    state.provider_creator,
                    module_path[0].binding_registry,
                    state.options,
                    state,
                )
            state = state.state_by_module[module_path[0]]
            module_path = module_path[1:]
            if cache_provider:
                return state.provider_creator.get_provider(
                    Target(binding.target.type, binding.target.annotation), state)
        return self._create_from_binding(binding, state)

    def _create_from_binding(self,
                             binding: RegisteredBinding[Binding[InjectedT]],
                             state: InjectionState) -> Provider[InjectedT]:
        for adapter in self._binding_to_provider_adapters:
            if adapter.accept(binding.raw_binding, state):
                return adapter.create(binding, state)
        raise BindingError(f"Could not find a BindingToProviderAdapter for {binding!r}")
