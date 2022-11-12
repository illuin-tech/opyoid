import os
from unittest import TestCase
from unittest.mock import ANY

from opyoid import conditional_on_env_var, Module
from opyoid.frozen_target import FrozenTarget


class MyType:
    pass


class TestConditionalOnEnvVar(TestCase):
    def setUp(self) -> None:
        self.env_var_name = "my_env_var"

    def tearDown(self) -> None:
        os.environ.pop(self.env_var_name, None)

    def test_decorator_disables_module_if_variable_is_not_set(self):
        @conditional_on_env_var(self.env_var_name)
        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyType)

        module = MyModule()
        module.configure_once()
        self.assertEqual({}, module.binding_registry.get_bindings_by_target())

    def test_decorator_disables_module_if_variable_is_set_to_wrong_value(self):
        os.environ[self.env_var_name] = "false"

        @conditional_on_env_var(self.env_var_name, expected_value="true")
        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyType)

        module = MyModule()
        module.configure_once()
        self.assertEqual({}, module.binding_registry.get_bindings_by_target())

    def test_decorator_enables_module_if_variable_is_set(self):
        os.environ[self.env_var_name] = "true"

        @conditional_on_env_var(self.env_var_name)
        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyType)

        module = MyModule()
        module.configure_once()
        self.assertEqual({FrozenTarget(MyType): ANY}, module.binding_registry.get_bindings_by_target())

    def test_decorator_enables_module_if_variable_is_set_to_expected_value(self):
        os.environ[self.env_var_name] = "true"

        @conditional_on_env_var(self.env_var_name, expected_value="true")
        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyType)

        module = MyModule()
        module.configure_once()
        self.assertEqual({FrozenTarget(MyType): ANY}, module.binding_registry.get_bindings_by_target())
