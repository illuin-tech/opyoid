import unittest

from illuin_inject import PerLookupScope, SingletonScope
from illuin_inject.bindings import FactoryBinding
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory


class MyType:
    pass


class MyFactory(Factory[MyType]):
    def create(self) -> MyType:
        return MyType()


class TestFactoryBinding(unittest.TestCase):
    def test_default_bind(self):
        binding = FactoryBinding(MyType, MyFactory)

        self.assertEqual(MyType, binding.target_type)
        self.assertEqual(MyFactory, binding.bound_factory)
        self.assertEqual(SingletonScope, binding.scope)
        self.assertIsNone(binding.annotation)

    def test_bind_factory_instance_with_scope_raises_exception(self):
        with self.assertRaises(BindingError):
            FactoryBinding(MyType, MyFactory(), PerLookupScope)
