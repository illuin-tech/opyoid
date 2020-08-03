from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .class_binding import ClassBinding


# pylint: disable=no-self-use, unused-argument
class ClassBindingToProviderAdapter(BindingToProviderAdapter[ClassBinding]):
    """Creates a Provider from an ClassBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self, binding: ClassBinding[InjectedT], state: InjectionState) -> Provider:
        new_target = Target(binding.bound_type, binding.annotation)
        return state.provider_creator.get_provider(new_target, state)
