import logging
import os
import re
from typing import Any, Optional

from opyoid.bindings import FromInstanceProvider
from opyoid.exceptions import IncompatibleProviderFactory
from opyoid.injection_context import InjectionContext
from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .provider_factory import ProviderFactory


class FromEnvVarProviderFactory(ProviderFactory):
    """Creates a Provider from an environment variable."""

    logger = logging.getLogger(__name__)

    def create(self, context: InjectionContext[InjectedT]) -> Provider[InjectedT]:
        if (
            context.injection_state.options.use_env_vars
            and context.current_parameter is not None
            and context.current_class is not None
            and context.target.type in (str, int, float, bool)
        ):
            env_var_name = self._get_matching_env_var_name(context)
            if env_var_name is not None:
                converted_value = self._get_converted_value(env_var_name, context)
                return FromInstanceProvider(converted_value)
        raise IncompatibleProviderFactory

    def _get_matching_env_var_name(self, context: InjectionContext[InjectedT]) -> Optional[str]:
        expected_env_var = (
            f"{self._to_upper_case(context.current_class.__name__)}_"  # type: ignore[union-attr]
            f"{self._to_upper_case(context.target.named or context.current_parameter.name)}"  # type: ignore[union-attr]
        )
        return expected_env_var if expected_env_var in os.environ else None

    @staticmethod
    def _to_upper_case(string: str) -> str:
        return re.sub(
            r"([A-Z])([A-Z][a-z])|([a-z])([A-Z])|(\d)([A-Za-z])|([A-Za-z])(\d)",
            r"\1\3\5\7_\2\4\6\8",
            string,
        ).upper()

    @staticmethod
    def _get_converted_value(env_var_name: str, context: InjectionContext[InjectedT]) -> Any:
        value: str = os.environ[env_var_name]
        if context.target.type == bool:
            if value.lower() in ["true", "false", "0"]:
                return value.lower() == "true"
            if value == "1":
                return True
            raise ValueError(f"Could not coerce {value} from environment variable {env_var_name} into a boolean")
        return context.target.type(value)  # type: ignore[operator]
