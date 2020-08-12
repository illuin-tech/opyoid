import unittest

from opyoid import SingletonScope
from opyoid.bindings import ClassBinding


class MyType:
    pass


class TestClassBinding(unittest.TestCase):
    def test_default_bind(self):
        binding = ClassBinding(MyType)

        self.assertEqual(MyType, binding.target_type)
        self.assertEqual(MyType, binding.bound_type)
        self.assertEqual(SingletonScope, binding.scope)
        self.assertIsNone(binding.annotation)
