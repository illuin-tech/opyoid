import logging
from inspect import Parameter, signature
from typing import Dict, List, Optional, Type

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.instance_binding import FromInstanceProvider
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_state import InjectionState
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.typings import EMPTY, InjectedT
from .from_class_provider import FromClassProvider
from .self_binding import SelfBinding


# pylint: disable=no-self-use, unused-argument
class SelfBindingToProviderAdapter(BindingToProviderAdapter[SelfBinding]):
    """Creates a Provider from a SelfBinding."""

    logger = logging.getLogger(__name__)

    def accept(self, binding: Binding[InjectedT], state: InjectionState) -> bool:
        return isinstance(binding, SelfBinding)

    def create(self, binding: SelfBinding[InjectedT], state: InjectionState) -> Provider:
        parameters = signature(binding.target_type.__init__).parameters
        positional_providers: List[Provider] = []
        args_provider: Optional[Provider[List]] = None
        keyword_providers: Dict[str, Provider] = {}
        # Ignore 'self'
        for parameter in list(parameters.values())[1:]:
            # Ignore '**kwargs'
            if parameter.kind == Parameter.VAR_KEYWORD:
                continue

            if parameter.kind == Parameter.VAR_POSITIONAL:
                # *args
                args_provider = self._get_positional_parameter_provider(parameter, binding.target_type, state)
                continue
            parameter_provider = self._get_parameter_provider(parameter, binding.target_type, state)
            if parameter.kind == Parameter.KEYWORD_ONLY:
                # After *args
                keyword_providers[parameter.name] = parameter_provider
            else:
                # Before *args
                positional_providers.append(parameter_provider)
        unscoped_provider = FromClassProvider(
            binding.target_type,
            positional_providers,
            args_provider,
            keyword_providers,
        )
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
        default_value = parameter.default if parameter.default is not Parameter.empty else EMPTY
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_annotated(parameter.annotation):
                target = Target(parameter.annotation.original_type, parameter.annotation.annotation, default_value)
            else:
                target = Target(parameter.annotation, None, default_value)
            try:
                return state.provider_creator.get_provider(target, state)
            except NoBindingFound:
                pass
        if parameter.default is not Parameter.empty:
            return FromInstanceProvider(parameter.default)
        raise NonInjectableTypeError(f"Could not find a binding or a default value for {parameter.name}: "
                                     f"{parameter.annotation} required by {current_class}")

    def _get_positional_parameter_provider(self,
                                           parameter: Parameter,
                                           current_class: Type,
                                           state: InjectionState) -> Provider[List]:
        if parameter.annotation is Parameter.empty:
            return FromInstanceProvider([])
        if TypeChecker.is_annotated(parameter.annotation):
            target = Target(List[parameter.annotation.original_type], parameter.annotation.annotation, [])
        else:
            target = Target(List[parameter.annotation], default=[])
        try:
            return state.provider_creator.get_provider(target, state)
        except NoBindingFound:
            self.logger.debug(f"Could not find a binding for *{parameter.name}: {parameter.annotation} required by "
                              f"{current_class}, will inject nothing")
            return FromInstanceProvider([])
