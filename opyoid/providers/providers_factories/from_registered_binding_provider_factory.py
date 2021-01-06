import logging
from typing import List

from opyoid.bindings import Binding, BindingToProviderAdapter, ClassBindingToProviderAdapter, \
    InstanceBindingToProviderAdapter, MultiBindingToProviderAdapter, ProviderBindingToProviderAdapter, \
    SelfBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import BindingError
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.utils import InjectedT


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
               context: InjectionContext[InjectedT],
               cache_provider: bool = True) -> Provider[InjectedT]:
        module_path = binding.source_path
        while module_path:
            state = context.injection_state
            if module_path[0] not in state.state_by_module:
                state.state_by_module[module_path[0]] = InjectionState(
                    state.provider_creator,
                    module_path[0].binding_registry,
                    state.options,
                    state,
                )
            context = context.get_new_state_context(state.state_by_module[module_path[0]])
            module_path = module_path[1:]
            if cache_provider:
                return context.get_provider()
        return self._create_from_binding(binding, context)

    def _create_from_binding(self,
                             binding: RegisteredBinding[Binding[InjectedT]],
                             context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        for adapter in self._binding_to_provider_adapters:
            if adapter.accept(binding.raw_binding, context):
                return adapter.create(binding, context)
        raise BindingError(f"Could not find a BindingToProviderAdapter for {binding!r}")
