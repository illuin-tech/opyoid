from opyoid.bindings import RegisteredBinding, SelfBinding, SelfBindingToProviderAdapter
from opyoid.exceptions import IncompatibleProviderFactory
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import EMPTY, InjectedT
from .provider_factory import ProviderFactory


class JitProviderFactory(ProviderFactory):
    def __init__(self) -> None:
        self._provider_factory = SelfBindingToProviderAdapter()

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if (
            context.injection_state.options.auto_bindings
            and context.target.default is EMPTY
            and context.allow_jit_provider
            and isinstance(context.target.type, type)
        ):
            return self._provider_factory.create(
                RegisteredBinding(SelfBinding(context.target.type, named=context.target.named), None), context
            )
        raise IncompatibleProviderFactory
