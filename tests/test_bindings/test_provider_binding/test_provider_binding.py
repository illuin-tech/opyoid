import unittest

from opyoid import PerLookupScope, Provider, SingletonScope
from opyoid.bindings import ProviderBinding
from opyoid.exceptions import BindingError


class MyType:
    pass


class MyProvider(Provider[MyType]):
    def get(self) -> MyType:
        return MyType()


class TestProviderBinding(unittest.TestCase):
    def test_default_bind(self):
        binding = ProviderBinding(MyType, MyProvider)

        self.assertEqual(MyType, binding.target_type)
        self.assertEqual(MyProvider, binding.bound_provider)
        self.assertEqual(SingletonScope, binding.scope)
        self.assertIsNone(binding.annotation)

    def test_bind_provider_instance_with_scope_raises_exception(self):
        with self.assertRaises(BindingError):
            ProviderBinding(MyType, MyProvider(), PerLookupScope)
