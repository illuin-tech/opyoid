import logging
import sys
from inspect import Parameter, signature
from typing import Any, Callable, Dict, List, Optional, Tuple

from opyoid.bindings.instance_binding import FromInstanceProvider
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.target import Target
from opyoid.type_checker import TypeChecker
from opyoid.utils import EMPTY, get_class_full_name, InjectedT


class ParametersProvider:
    """Creates Providers from a callable."""

    logger = logging.getLogger(__name__)

    def get_parameters_provider(
        self,
        type_or_function: Callable[..., InjectedT],
        context: InjectionContext[InjectedT],
    ) -> Tuple[List[Provider[Any]], Optional[Provider[List[Any]]], Dict[str, Provider[Any]]]:
        if sys.version_info[:2] < (3, 9) and isinstance(type_or_function, type):  # pragma: nocover
            parameters = list(signature(type_or_function.__init__).parameters.values())[1:]
        else:
            parameters = list(signature(type_or_function).parameters.values())

        positional_providers: List[Provider[Any]] = []
        args_provider: Optional[Provider[List[Any]]] = None
        keyword_providers: Dict[str, Provider[Any]] = {}
        for parameter in parameters:
            context.current_parameter = parameter
            # Ignore '**kwargs'
            if parameter.kind == Parameter.VAR_KEYWORD:
                continue

            if parameter.kind == Parameter.VAR_POSITIONAL:
                # *args
                args_provider = self._get_positional_parameter_provider(parameter, type_or_function, context)
                continue
            parameter_provider = self._get_parameter_provider(parameter, type_or_function, context)
            if parameter.kind == Parameter.KEYWORD_ONLY:
                # After *args
                keyword_providers[parameter.name] = parameter_provider
            else:
                # Before *args
                positional_providers.append(parameter_provider)
        return positional_providers, args_provider, keyword_providers

    def _get_parameter_provider(
        self,
        parameter: Parameter,
        type_or_function: Callable[..., InjectedT],
        context: InjectionContext[InjectedT],
    ) -> Provider[InjectedT]:
        default_value = parameter.default if parameter.default is not Parameter.empty else EMPTY
        if parameter.annotation is not Parameter.empty:
            if TypeChecker.is_named(parameter.annotation):
                provider: Optional[Provider[InjectedT]] = self._get_provider(
                    [
                        Target(
                            parameter.annotation.original_type,
                            parameter.annotation.name,
                            default_value,
                        )
                    ],
                    context,
                )
            else:
                provider = self._get_provider(
                    [
                        Target(parameter.annotation, parameter.name, default_value),
                        Target(parameter.annotation, None, default_value),
                    ],
                    context,
                )
            if provider:
                return provider
        if parameter.default is not Parameter.empty:
            return FromInstanceProvider(parameter.default)
        raise NonInjectableTypeError(
            f"Could not find a binding or a default value for {parameter.name}: "
            f"{get_class_full_name(parameter.annotation)} required by {type_or_function}"
        )

    def _get_positional_parameter_provider(
        self,
        parameter: Parameter,
        type_or_function: Callable[..., InjectedT],
        context: InjectionContext[InjectedT],
    ) -> Provider[List[InjectedT]]:
        if parameter.annotation is Parameter.empty:
            return FromInstanceProvider([])
        if TypeChecker.is_named(parameter.annotation):
            provider: Optional[Provider[List[InjectedT]]] = self._get_provider(
                [
                    Target(
                        List[parameter.annotation.original_type],  # type: ignore[name-defined]
                        parameter.annotation.name,
                        default=[],
                    )
                ],
                context,
            )
        else:
            provider = self._get_provider(
                [
                    Target(List[parameter.annotation], parameter.name, default=[]),  # type: ignore[name-defined]
                    Target(List[parameter.annotation], default=[]),  # type: ignore[name-defined]
                ],
                context,
            )
        if provider:
            return provider
        self.logger.debug(
            f"Could not find a binding for *{parameter.name}: {parameter.annotation} required by "
            f"{type_or_function}, will inject nothing"
        )
        return FromInstanceProvider([])

    @staticmethod
    def _get_provider(
        targets: List[Target[InjectedT]], parent_context: InjectionContext[Any]
    ) -> Optional[Provider[InjectedT]]:
        for target_index, target in enumerate(targets):
            context = parent_context.get_child_context(target, allow_jit_provider=target_index == len(targets) - 1)
            context.current_class = parent_context.current_class
            context.current_parameter = parent_context.current_parameter
            try:
                return context.get_provider()
            except NoBindingFound:
                pass
        return None
