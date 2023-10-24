from typing import Any, cast
from unittest import TestCase
from unittest.mock import ANY, create_autospec

from opyoid import Provider
from opyoid.bindings.self_binding.parameters_provider import ParametersProvider
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState


class TestParametersProvider(TestCase):
    def setUp(self):
        self.provider = ParametersProvider()
        self.context = InjectionContext(ANY, create_autospec(InjectionState, spec_set=True))

    def test_get_parameters_provider_with_default_constructor(self):
        class MyClass:
            def __init__(self, *args, **kwargs):
                pass

        (
            positional_providers,
            args_provider,
            keyword_providers,
        ) = self.provider.get_parameters_provider(MyClass, self.context)
        self.assertEqual([], positional_providers)
        self.assertEqual([], cast(Provider[Any], args_provider).get())
        self.assertEqual({}, keyword_providers)
