import unittest
from unittest.mock import create_autospec

from illuin_inject.bindings import FromFactoryProvider
from illuin_inject.provider import Provider


class TestFromFactoryProvider(unittest.TestCase):
    def test_provider(self):
        factory_provider = create_autospec(Provider, spec_set=True)
        provider = FromFactoryProvider(factory_provider)
        instance = provider.get()
        self.assertIs(instance, factory_provider.get.return_value.create.return_value)
