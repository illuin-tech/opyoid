from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .from_instance_provider import FromInstanceProvider
from .instance_binding import InstanceBinding


class InstanceBindingToProviderAdapter(BindingToProviderAdapter):
    """Creates a Provider from an InstanceBinding."""

    def create(
        self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        if isinstance(binding.raw_binding, InstanceBinding):
            return FromInstanceProvider(binding.raw_binding.bound_instance)
        raise IncompatibleAdapter
