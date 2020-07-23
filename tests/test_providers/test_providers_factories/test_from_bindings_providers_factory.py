import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, PerLookupScope, Provider
from illuin_inject.bindings import Binding, BindingRegistry
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.providers import ProviderCreator
from illuin_inject.providers.providers_factories import FromBindingProviderFactory
from illuin_inject.target import Target


class MyType:
    pass


class TestFromBindingsProvidersFactory(unittest.TestCase):
    def setUp(self):
        self.binding_registry = create_autospec(BindingRegistry, spec_set=True)
        self.providers_factory = FromBindingProviderFactory(
            self.binding_registry,
        )
        self.provider_creator = create_autospec(ProviderCreator, spec_set=True)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_unknown_binding_type_raises_binding_error(self):
        self.binding_registry.get_binding.return_value = Binding()
        with self.assertRaises(BindingError):
            self.providers_factory.create(Target(str), self.provider_creator)

    def test_accept(self):
        self.binding_registry.__contains__.side_effect = [
            True,
            False,
        ]

        self.assertTrue(self.providers_factory.accept(Target(str)))
        self.assertFalse(self.providers_factory.accept(Target(int)))
        self.assertEqual(
            [
                call(Target(str)),
                call(Target(int)),
            ],
            self.binding_registry.__contains__.call_args_list
        )

    def test_create_creates_provider_for_instance_binding(self):
        binding = InstanceBinding(MyType, MyType())
        self.binding_registry.get_binding.return_value = binding

        provider = self.providers_factory.create(Target(MyType), self.provider_creator)
        instance = provider.get()
        self.assertIs(binding.bound_instance, instance)

    def test_create_creates_provider_for_class_binding(self):
        binding = ClassBinding(MyType)
        self.provider_creator.get_provider.return_value = self.mock_scope_provider
        self.binding_registry.get_binding.return_value = binding

        provider = self.providers_factory.create(Target(MyType), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_creates_provider_for_factory_binding(self):
        factory = create_autospec(Factory, spec_set=True)
        factory.create.return_value = MyType()
        binding = FactoryBinding(MyType, factory)
        self.binding_registry.get_binding.return_value = binding
        self.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.providers_factory.create(Target(MyType), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)
