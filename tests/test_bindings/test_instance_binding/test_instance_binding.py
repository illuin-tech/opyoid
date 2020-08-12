import unittest

from opyoid import InstanceBinding


class MyType:
    pass


class TestInstanceBinding(unittest.TestCase):
    def test_default_bind(self):
        instance = MyType()
        binding = InstanceBinding(MyType, instance)

        self.assertEqual(MyType, binding.target_type)
        self.assertIs(instance, binding.bound_instance)
        self.assertIsNone(binding.annotation)
