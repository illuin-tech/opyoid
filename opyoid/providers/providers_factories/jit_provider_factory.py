from opyoid.bindings import RegisteredBinding, SelfBinding, SelfBindingToProviderAdapter
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import EMPTY, InjectedT
from .provider_factory import ProviderFactory


class JitProviderFactory(ProviderFactory):
    def __init__(self):
        self._provider_factory = SelfBindingToProviderAdapter()

    def accept(self, context: InjectionContext[InjectedT]) -> bool:
        return context.injection_state.options.auto_bindings \
               and context.target.default is EMPTY \
               and not isinstance(context.target.type, str)

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        return self._provider_factory.create(
            RegisteredBinding(SelfBinding(context.target.type, named=context.target.named)), context)
