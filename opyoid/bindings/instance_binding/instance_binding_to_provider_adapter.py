from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.typings import InjectedT
from .from_instance_provider import FromInstanceProvider
from .instance_binding import InstanceBinding


# pylint: disable=no-self-use, unused-argument
class InstanceBindingToProviderAdapter(BindingToProviderAdapter[InstanceBinding]):
    """Creates a Provider from an InstanceBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, InstanceBinding)

    def create(self, binding: InstanceBinding[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        return FromInstanceProvider(binding.bound_instance)
