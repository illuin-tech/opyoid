from inspect import Parameter, signature
from typing import Dict, List, TYPE_CHECKING, Type

from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from illuin_inject.bindings.instance_binding import FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.provider import Provider
from illuin_inject.target import Target
from illuin_inject.type_checker import TypeChecker
from illuin_inject.typings import InjectedT
from .class_binding import ClassBinding
from .from_class_provider import FromClassProvider

if TYPE_CHECKING:
    from illuin_inject.providers.providers_creator import ProvidersCreator


# pylint: disable=no-self-use
class ClassBindingToProviderAdapter(BindingToProviderAdapter[ClassBinding]):
    """Creates a Provider from an ClassBinding."""

    def accept(self, binding: Binding[InjectedT]) -> bool:
        return isinstance(binding, ClassBinding)

    def create(self, binding: ClassBinding[InjectedT], providers_creator: "ProvidersCreator") -> Provider:
        parameters = signature(binding.bound_type.__init__).parameters
        args: List[Provider] = []
        kwargs: Dict[str, Provider] = {}
        # Ignore 'self'
        for parameter in list(parameters.values())[1:]:
            # Ignore '*args' and '**kwargs'
            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                continue

            parameter_provider = self._get_parameter_provider(parameter, binding.bound_type, providers_creator)
            if parameter.kind == Parameter.KEYWORD_ONLY:
                kwargs[parameter.name] = parameter_provider
            else:
                args.append(parameter_provider)
        unscoped_provider = FromClassProvider(binding.bound_type, args, kwargs)
        return binding.scope.get_scoped_provider(unscoped_provider)

    @staticmethod
    def _get_parameter_provider(parameter: Parameter,
                                current_class: Type,
                                providers_creator: "ProvidersCreator") -> Provider:
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_annotated(parameter.annotation):
                target = Target(parameter.annotation.original_type, parameter.annotation.annotation)
            else:
                target = Target(parameter.annotation, None)
            try:
                return providers_creator.get_providers(target)[-1]
            except NoBindingFound:
                pass
        if parameter.default is not Parameter.empty:
            return FromInstanceProvider(parameter.default)
        raise NonInjectableTypeError(f"Could not find binding or default value for {parameter.name}: "
                                     f"{parameter.annotation} required by {current_class}")
