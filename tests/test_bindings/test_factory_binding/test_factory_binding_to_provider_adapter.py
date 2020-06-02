import unittest
from unittest.mock import create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, ThreadScope
from illuin_inject.bindings import FactoryBindingToProviderAdapter
from illuin_inject.factory import Factory
from illuin_inject.provider import Provider
from illuin_inject.providers import ProvidersCreator
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider
from illuin_inject.target import Target


class MyType:
    def __init__(self):
        pass


class TestFactoryBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = FactoryBindingToProviderAdapter()
        self.providers_creator = create_autospec(ProvidersCreator, spec_set=True)
        self.factory = create_autospec(Factory, spec_set=True)
        self.instance = MyType()
        self.factory.create.return_value = self.instance
        self.unused_provider = create_autospec(Provider, spec_set=True)
        self.factory_provider = create_autospec(Provider, spec_set=True)
        self.factory_provider.get.return_value = self.factory

    def test_accept_factory_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(FactoryBinding(MyType, create_autospec(Factory))))

    def test_accept_non_factory_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(ClassBinding(MyType)))
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType())))

    def test_create_returns_provider(self):
        self.providers_creator.get_providers.return_value = [
            self.unused_provider,
            self.factory_provider,
        ]

        provider = self.adapter.create(FactoryBinding(MyType, self.factory), self.providers_creator)

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.providers_creator.get_providers.assert_called_once_with(
            Target(self.factory)
        )

    def test_create_annotated_provider(self):
        self.providers_creator.get_providers.return_value = [
            self.unused_provider,
            self.factory_provider,
        ]

        provider = self.adapter.create(
            FactoryBinding(MyType, self.factory, annotation="my_annotation"),
            self.providers_creator,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.providers_creator.get_providers.assert_called_once_with(
            Target(self.factory, annotation="my_annotation")
        )

    def test_create_scoped_provider(self):
        self.providers_creator.get_providers.return_value = [
            self.unused_provider,
            self.factory_provider,
        ]

        provider = self.adapter.create(
            FactoryBinding(MyType, self.factory, scope=ThreadScope),
            self.providers_creator,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.providers_creator.get_providers.assert_called_once_with(
            Target(self.factory)
        )
        self.assertIsInstance(provider, ThreadScopedProvider)
