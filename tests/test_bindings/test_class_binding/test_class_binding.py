import unittest

from opyoid import BindingError, SingletonScope
from opyoid.bindings import ClassBinding


class MyType:
    pass


class MySubType(MyType):
    pass


class TestClassBinding(unittest.TestCase):
    def test_bind_class_to_itself_raises_exception(self):
        with self.assertRaises(BindingError):
            ClassBinding(MyType, MyType)

    def test_default_bind(self):
        binding = ClassBinding(MyType, MySubType)

        self.assertEqual(MyType, binding.target_type)
        self.assertEqual(MySubType, binding.bound_class)
        self.assertEqual(SingletonScope, binding.scope)
        self.assertIsNone(binding.named)
