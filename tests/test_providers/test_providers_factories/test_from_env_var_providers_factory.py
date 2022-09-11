import os
import unittest
from inspect import signature
from unittest.mock import create_autospec

from opyoid.bindings import BindingRegistry
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.providers.providers_factories import FromEnvVarProviderFactory
from opyoid.target import Target


class MyType:
    def __init__(self, arg: bool):
        self.arg = arg


class TestFromEnvVarProviderFactory(unittest.TestCase):
    def setUp(self):
        self.provider_factory = FromEnvVarProviderFactory()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.context = InjectionContext(
            Target(bool, named="arg"),
            self.state,
            current_class=MyType,
            current_parameter=signature(MyType).parameters.get("arg"),
        )

    def test_convert_bool_from_invalid_value(self):
        os.environ["MY_TYPE_ARG"] = "invalid_value"
        with self.assertRaises(ValueError):
            self.provider_factory.create(self.context)
