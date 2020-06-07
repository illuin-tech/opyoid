from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .from_instance_provider import FromInstanceProvider
from .instance_binding import InstanceBinding


# pylint: disable=no-self-use, unused-argument
class InstanceBindingToProviderAdapter(BindingToProviderAdapter[InstanceBinding]):
    """Creates a Provider from an InstanceBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, InstanceBinding)

    def create(self, binding: InstanceBinding[InjectedT], state: InjectionState) -> Provider[InjectedT]:
        return FromInstanceProvider(binding.bound_instance)
