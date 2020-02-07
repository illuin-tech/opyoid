import unittest

from illuin_inject import PerLookupScope


class MyClass:
    pass


def provider():
    return MyClass()


class TestPerLookupScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = PerLookupScope()

    def test_get_returns_instance(self):
        instance = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance, MyClass)

    def test_multiple_get_return_new_instances(self):
        instance_1 = self.scope.get(MyClass, provider)
        instance_2 = self.scope.get(MyClass, provider)

        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_2, MyClass)
        self.assertIsNot(instance_1, instance_2)
