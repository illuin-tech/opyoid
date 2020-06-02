import unittest

from illuin_inject import PerLookupScope
from illuin_inject.bindings import FromClassProvider


class MyType:
    pass


class TestPerLookupScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = PerLookupScope()
        self.class_provider = FromClassProvider(MyType, [], {})

    def test_get_scoped_provider_returns_unscoped_provider(self):
        scoped_provider = self.scope.get_scoped_provider(self.class_provider)

        instance_1 = scoped_provider.get()
        instance_2 = scoped_provider.get()

        self.assertIsNot(instance_1, instance_2)
        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
