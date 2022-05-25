import unittest

from opyoid import ImmediateScope
from opyoid.bindings import FromCallableProvider
from opyoid.scopes.singleton_scoped_provider import SingletonScopedProvider


class MyType:
    pass


class TestImmediateScope(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = ImmediateScope()
        self.class_provider = FromCallableProvider(MyType, [], None, {})

    def test_get_scoped_provider_returns_singleton_scoped_provider(self):
        scoped_provider = self.scope.get_scoped_provider(self.class_provider)

        self.assertIsInstance(scoped_provider, SingletonScopedProvider)
        instance = scoped_provider.get()
        self.assertIsInstance(instance, MyType)

    def test_creating_scoped_provider_instantiates_instance(self):
        class MyOtherType:
            created_count = 0

            def __init__(self):
                MyOtherType.created_count += 1

        class_provider = FromCallableProvider(MyOtherType, [], None, {})
        self.scope.get_scoped_provider(class_provider)
        self.assertEqual(1, MyOtherType.created_count)
