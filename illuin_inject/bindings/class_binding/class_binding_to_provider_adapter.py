from inspect import Parameter, signature
from typing import Dict, List, Type

from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.bindings.instance_binding import FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .class_binding import ClassBinding
from .from_class_provider import FromClassProvider


# pylint: disable=no-self-use, unused-argument
class ClassBindingToProviderAdapter(BindingToProviderAdapter[ClassBinding]):
    """Creates a Provider from an ClassBinding."""

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self, binding: ClassBinding[InjectedT], state: InjectionState) -> Provider:
        parameters = signature(binding.bound_type.__init__).parameters
        args: List[Provider] = []
        kwargs: Dict[str, Provider] = {}
        # Ignore 'self'
        for parameter in list(parameters.values())[1:]:
            # Ignore '*args' and '**kwargs'
            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                continue

            parameter_provider = self._get_parameter_provider(parameter, binding.bound_type, state)
            if parameter.kind == Parameter.KEYWORD_ONLY:
                kwargs[parameter.name] = parameter_provider
            else:
                args.append(parameter_provider)
        unscoped_provider = FromClassProvider(binding.bound_type, args, kwargs)
        try:
            scope_provider = state.provider_creator.get_provider(Target(binding.scope), state)
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding!r}: they are no bindings for"
                                         f" {binding.scope.__name__!r}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)

    @staticmethod
    def _get_parameter_provider(parameter: Parameter,
                                current_class: Type,
                                state: InjectionState) -> Provider:
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_annotated(parameter.annotation):
                target = Target(parameter.annotation.original_type, parameter.annotation.annotation)
            else:
                target = Target(parameter.annotation, None)
            try:
                return state.provider_creator.get_provider(target, state)
            except NoBindingFound:
                pass
        if parameter.default is not Parameter.empty:
            return FromInstanceProvider(parameter.default)
        raise NonInjectableTypeError(f"Could not find binding or default value for {parameter.name}: "
                                     f"{parameter.annotation} required by {current_class}")
