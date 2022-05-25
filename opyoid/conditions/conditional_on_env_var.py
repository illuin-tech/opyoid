from typing import Callable, Type, TypeVar

from opyoid.bindings import AbstractModule
from .env_var_condition import EnvVarCondition

ModuleClassT = TypeVar("ModuleClassT", bound=Type[AbstractModule])


def conditional_on_env_var(env_var_name: str, *, expected_value: str = None) -> Callable[[ModuleClassT], ModuleClassT]:
    def add_condition_on_module(module: ModuleClassT) -> ModuleClassT:
        module.add_condition(EnvVarCondition(env_var_name, module, expected_value))
        return module

    return add_condition_on_module
