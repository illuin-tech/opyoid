from opyoid.bindings import SelfBinding, SelfBindingToProviderAdapter
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import EMPTY, InjectedT
from .provider_factory import ProviderFactory
from ...bindings.registered_binding import RegisteredBinding


class JitProviderFactory(ProviderFactory):
    def __init__(self):
        self.provider_factory = SelfBindingToProviderAdapter()

    def accept(self, target: Target[InjectedT], state: InjectionState) -> bool:
        return state.options.auto_bindings and target.default is EMPTY and not isinstance(target.type, str)

    def create(self, target: Target[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        return self.provider_factory.create(
            RegisteredBinding(SelfBinding(target.type, annotation=target.annotation)), state)
