from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
from .from_provider_provider import FromProviderProvider
from .provider_binding import ProviderBinding


# pylint: disable=no-self-use, unused-argument
class ProviderBindingToProviderAdapter(BindingToProviderAdapter[ProviderBinding]):
    """Creates a Provider from a ProviderBinding."""

    def accept(self, binding: Binding[InjectedT], context: InjectionContext) -> bool:
        return isinstance(binding, ProviderBinding)

    def create(self,
               binding: RegisteredBinding[ProviderBinding[InjectedT]],
               context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if isinstance(binding.raw_binding.bound_provider, Provider):
            return binding.raw_binding.bound_provider
        provider_target = Target(binding.raw_binding.bound_provider, binding.raw_binding.named)
        provider_context = context.get_child_context(provider_target)
        provider_provider = provider_context.get_provider()
        unscoped_provider = FromProviderProvider(
            provider_provider,
        )
        scope_context = context.get_child_context(Target(binding.raw_binding.scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding}: they are no bindings for"
                                         f"the scope {binding.raw_binding.scope}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)
