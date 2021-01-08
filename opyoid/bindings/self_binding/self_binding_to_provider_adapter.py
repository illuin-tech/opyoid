import logging
from inspect import Parameter, signature
from typing import Dict, List, Optional, Type

from opyoid.bindings.binding import Binding
from opyoid.bindings.binding_to_provider_adapter import BindingToProviderAdapter
from opyoid.bindings.instance_binding import FromInstanceProvider
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import EMPTY, InjectedT
from .from_class_provider import FromClassProvider
from .self_binding import SelfBinding


# pylint: disable=no-self-use, unused-argument
class SelfBindingToProviderAdapter(BindingToProviderAdapter[SelfBinding]):
    """Creates a Provider from a SelfBinding."""

    logger = logging.getLogger(__name__)

    def accept(self, binding: Binding[InjectedT], context: InjectionContext) -> bool:
        return isinstance(binding, SelfBinding)

    def create(self,
               binding: RegisteredBinding[SelfBinding[InjectedT]],
               context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        parameters = signature(binding.target.type.__init__).parameters
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
                args_provider = self._get_positional_parameter_provider(parameter, binding.target.type, context)
                continue
            parameter_provider = self._get_parameter_provider(parameter, binding.target.type, context)
            if parameter.kind == Parameter.KEYWORD_ONLY:
                # After *args
                keyword_providers[parameter.name] = parameter_provider
            else:
                # Before *args
                positional_providers.append(parameter_provider)
        unscoped_provider = FromClassProvider(
            binding.target.type,
            positional_providers,
            args_provider,
            keyword_providers,
        )
        scope_context = context.get_child_context(Target(binding.raw_binding.scope))
        try:
            scope_provider = scope_context.get_provider()
        except NoBindingFound:
            raise NonInjectableTypeError(f"Could not create a provider for {binding!r}: they are no bindings for"
                                         f" {binding.raw_binding.scope.__name__!r}")
        return scope_provider.get().get_scoped_provider(unscoped_provider)

    def _get_parameter_provider(self,
                                parameter: Parameter,
                                current_class: Type,
                                context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        default_value = parameter.default if parameter.default is not Parameter.empty else EMPTY
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_named(parameter.annotation):
                provider = self._get_provider([
                    Target(parameter.annotation.original_type, parameter.annotation.name, default_value)], context)
            else:
                provider = self._get_provider([
                    Target(parameter.annotation, parameter.name, default_value),
                    Target(parameter.annotation, None, default_value),
                ], context)
            if provider:
                return provider
        if parameter.default is not Parameter.empty:
            return FromInstanceProvider(parameter.default)
        raise NonInjectableTypeError(f"Could not find a binding or a default value for {parameter.name}: "
                                     f"{parameter.annotation} required by {current_class}")

    def _get_positional_parameter_provider(self,
                                           parameter: Parameter,
                                           current_class: Type,
                                           context: InjectionContext[InjectedT]) -> Provider[List[InjectedT]]:
        if parameter.annotation is Parameter.empty:
            return FromInstanceProvider([])
        if TypeChecker.is_named(parameter.annotation):
            provider = self._get_provider([
                Target(List[parameter.annotation.original_type], parameter.annotation.name, default=[])
            ], context)
        else:
            provider = self._get_provider([
                Target(List[parameter.annotation], parameter.name, default=[]),
                Target(List[parameter.annotation], default=[]),
            ], context)
        if provider:
            return provider
        self.logger.debug(f"Could not find a binding for *{parameter.name}: {parameter.annotation} required by "
                          f"{current_class}, will inject nothing")
        return FromInstanceProvider([])

    @staticmethod
    def _get_provider(targets: List[Target[InjectedT]],
                      parent_context: InjectionContext) -> Optional[Provider[InjectedT]]:
        for target in targets:
            context = parent_context.get_child_context(target)
            try:
                return context.get_provider()
            except NoBindingFound:
                pass
        return None
