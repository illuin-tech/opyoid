from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
from .class_binding import ClassBinding


class ClassBindingToProviderAdapter(BindingToProviderAdapter):
    """Creates a Provider from an ClassBinding."""

    def create(
        self, binding: RegisteredBinding[InjectedT], context: InjectionContext[InjectedT]
    ) -> Provider[InjectedT]:
        if isinstance(binding.raw_binding, ClassBinding):
            new_target: Target[InjectedT] = Target(binding.raw_binding.bound_class, binding.raw_binding.named)
            new_context = context.get_child_context(new_target)
            return new_context.get_provider()
        raise IncompatibleAdapter
