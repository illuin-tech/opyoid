from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.typings import InjectedT
from .class_binding import ClassBinding


# pylint: disable=no-self-use, unused-argument
class ClassBindingToProviderAdapter(BindingToProviderAdapter[ClassBinding]):
    """Creates a Provider from an ClassBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self, binding: ClassBinding[InjectedT], state: InjectionState) -> Provider:
        new_target = Target(binding.bound_type, binding.annotation)
        return state.provider_creator.get_provider(new_target, state)
