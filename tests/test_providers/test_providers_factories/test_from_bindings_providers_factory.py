import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, PerLookupScope, Provider, SelfBinding
from illuin_inject.bindings import Binding, BindingRegistry
from illuin_inject.bindings.registered_binding import RegisteredBinding
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.injection_state import InjectionState
from illuin_inject.providers import ProviderCreator
from illuin_inject.providers.providers_factories import FromBindingProviderFactory
from illuin_inject.target import Target


class MyType:
    pass

class OtherType(MyType):
    pass


class TestFromBindingsProvidersFactory(unittest.TestCase):
    def setUp(self):
        self.binding_registry = create_autospec(BindingRegistry, spec_set=True)
        self.providers_factory = FromBindingProviderFactory()
        self.provider_creator = create_autospec(ProviderCreator, spec_set=True)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope
        self.state = InjectionState(
            self.provider_creator,
            self.binding_registry,
        )

    def test_unknown_binding_type_raises_binding_error(self):
        mock_binding = create_autospec(Binding, spec_set=True)
        self.binding_registry.get_binding.return_value = RegisteredBinding(mock_binding)
        self.binding_registry.__contains__.return_value = True
        with self.assertRaises(BindingError):
            self.providers_factory.create(Target(str), self.state)

    def test_accept(self):
        self.binding_registry.__contains__.side_effect = [
            True,
            False,
        ]

        self.assertTrue(self.providers_factory.accept(Target(str), self.state))
        self.assertFalse(self.providers_factory.accept(Target(int), self.state))
        self.assertEqual(
            [
                call(Target(str)),
                call(Target(int)),
            ],
            self.binding_registry.__contains__.call_args_list
        )

    def test_create_with_parent_binding(self):
        self.state.parent_state = InjectionState(create_autospec(ProviderCreator, spec_set=True), self.binding_registry)
        self.binding_registry.__contains__.side_effect = [
            False,
            True,
        ]

        self.assertTrue(self.providers_factory.accept(Target(str), self.state))
        self.assertEqual(
            [
                call(Target(str)),
                call(Target(str)),
            ],
            self.binding_registry.__contains__.call_args_list
        )

    def test_create_creates_provider_for_instance_binding(self):
        binding = InstanceBinding(MyType, MyType())
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.providers_factory.create(Target(MyType), self.state)
        instance = provider.get()
        self.assertIs(binding.bound_instance, instance)

    def test_create_creates_provider_for_class_binding(self):
        binding = ClassBinding(MyType, OtherType)
        mock_provider = create_autospec(Provider, spec_set=True)
        mock_provider.get.return_value = OtherType()
        self.provider_creator.get_provider.return_value = mock_provider
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.providers_factory.create(Target(MyType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, OtherType)

    def test_create_creates_provider_for_self_binding(self):
        binding = SelfBinding(MyType)
        self.provider_creator.get_provider.return_value = self.mock_scope_provider
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.providers_factory.create(Target(MyType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_creates_provider_for_factory_binding(self):
        factory = create_autospec(Factory, spec_set=True)
        factory.create.return_value = MyType()
        binding = FactoryBinding(MyType, factory)
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True
        self.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.providers_factory.create(Target(MyType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)
