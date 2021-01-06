from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .from_instance_provider import FromInstanceProvider
from .instance_binding import InstanceBinding


# pylint: disable=no-self-use, unused-argument
class InstanceBindingToProviderAdapter(BindingToProviderAdapter[InstanceBinding]):
    """Creates a Provider from an InstanceBinding."""

    def accept(self, binding: Binding[InjectedT], context: InjectionContext[InjectedT]) -> bool:
        return isinstance(binding, InstanceBinding)

    def create(self,
               binding: RegisteredBinding[InstanceBinding[InjectedT]],
               context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        return FromInstanceProvider(binding.raw_binding.bound_instance)
