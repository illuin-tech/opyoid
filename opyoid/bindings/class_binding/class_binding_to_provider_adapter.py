from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.utils import InjectedT
from .class_binding import ClassBinding


# pylint: disable=no-self-use, unused-argument
class ClassBindingToProviderAdapter(BindingToProviderAdapter[ClassBinding]):
    """Creates a Provider from an ClassBinding."""

    def accept(self, binding: Binding[InjectedT], context: InjectionContext[InjectedT]) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self,
               binding: RegisteredBinding[ClassBinding[InjectedT]],
               context: InjectionContext[InjectedT]) -> Provider:
        new_target = Target(binding.raw_binding.bound_type, binding.raw_binding.named)
        new_context = context.get_child_context(new_target)
        return new_context.get_provider()
