import unittest
from unittest.mock import create_autospec

from illuin_inject import ThreadScope
from illuin_inject.provider import Provider
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider


class TestThreadScope(unittest.TestCase):
    def test_get_scoped_provider_returns_thread_scoped_provider(self):
        inner_provider = create_autospec(Provider, spec_set=True)

        thread_scoped_provider = ThreadScope().get_scoped_provider(inner_provider)
        self.assertIsInstance(thread_scoped_provider, ThreadScopedProvider)

        instance = thread_scoped_provider.get()
        self.assertIs(inner_provider.get.return_value, instance)
        inner_provider.get.assert_called_once_with()
