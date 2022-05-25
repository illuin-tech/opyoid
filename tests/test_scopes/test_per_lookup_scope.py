import unittest

from opyoid import PerLookupScope
from opyoid.bindings import FromCallableProvider


class MyType:
    pass


class TestPerLookupScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = PerLookupScope()
        self.class_provider = FromCallableProvider(MyType, [], None, {})

    def test_get_scoped_provider_returns_unscoped_provider(self):
        scoped_provider = self.scope.get_scoped_provider(self.class_provider)

        instance_1 = scoped_provider.get()
        instance_2 = scoped_provider.get()

        self.assertIsNot(instance_1, instance_2)
        self.assertIsInstance(instance_1, MyType)
        self.assertIsInstance(instance_2, MyType)
