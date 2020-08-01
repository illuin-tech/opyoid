import unittest
from unittest.mock import create_autospec

from illuin_inject.bindings import FromProviderProvider
from illuin_inject.provider import Provider


class TestFromProviderProvider(unittest.TestCase):
    def test_provider(self):
        provider_provider = create_autospec(Provider, spec_set=True)
        provider = FromProviderProvider(provider_provider)
        instance = provider.get()
        self.assertIs(instance, provider_provider.get.return_value.get.return_value)
