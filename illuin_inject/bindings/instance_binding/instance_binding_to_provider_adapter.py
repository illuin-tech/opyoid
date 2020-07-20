from typing import TYPE_CHECKING

from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .from_instance_provider import FromInstanceProvider
from .instance_binding import InstanceBinding

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


# pylint: disable=no-self-use, unused-argument
class InstanceBindingToProviderAdapter(BindingToProviderAdapter[InstanceBinding]):
    """Creates a Provider from an InstanceBinding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, InstanceBinding)

    def create(self, binding: InstanceBinding[InjectedT], providers_creator: "ProvidersCreator") -> Provider[InjectedT]:
        return FromInstanceProvider(binding.bound_instance)
