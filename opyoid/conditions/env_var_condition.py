import logging
import os
from typing import Type

from opyoid.bindings import AbstractModule, Condition


class EnvVarCondition(Condition):
    logger = logging.getLogger(__name__)

    def __init__(self, env_var_name: str, module: Type[AbstractModule], expected_value: str = None):
        self._env_var_name = env_var_name
        self._module = module
        self._expected_value = expected_value

    def is_valid(self) -> bool:
        if self._env_var_name not in os.environ:
            self.logger.info(f"Disabling {self._module} as environment variable {self._env_var_name} is missing")
            return False
        env_value = os.getenv(self._env_var_name)
        if self._expected_value is not None and env_value != self._expected_value:
            self.logger.info(
                f"Disabling {self._module} as environment variable {self._env_var_name} is set to {env_value}"
            )
            return False
        return True
