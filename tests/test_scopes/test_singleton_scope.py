import unittest
from unittest.mock import create_autospec

from opyoid import SingletonScope
from opyoid.provider import Provider
from opyoid.scopes.singleton_scoped_provider import SingletonScopedProvider


class TestSingletonScope(unittest.TestCase):
    def test_get_scoped_provider_returns_singleton_scoped_provider(self):
        inner_provider = create_autospec(Provider, spec_set=True)

        singleton_scoped_provider = SingletonScope().get_scoped_provider(inner_provider)
        self.assertIsInstance(singleton_scoped_provider, SingletonScopedProvider)

        instance = singleton_scoped_provider.get()
        self.assertIs(inner_provider.get.return_value, instance)
        inner_provider.get.assert_called_once_with()
