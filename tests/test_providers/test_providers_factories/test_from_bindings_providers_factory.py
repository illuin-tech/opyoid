import unittest
from unittest.mock import call, create_autospec

from opyoid import ClassBinding, InstanceBinding, PerLookupScope, Provider, ProviderBinding, SelfBinding
from opyoid.bindings import Binding, BindingRegistry
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import BindingError
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.providers.providers_factories import FromBindingProviderFactory
from opyoid.target import Target


class MyType:
    pass


class OtherType(MyType):
    pass


class TestFromBindingsProviderFactory(unittest.TestCase):
    def setUp(self):
        self.binding_registry = create_autospec(BindingRegistry, spec_set=True)
        self.provider_factory = FromBindingProviderFactory()
        self.provider_creator = create_autospec(ProviderCreator, spec_set=True)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope
        self.state = InjectionState(
            self.provider_creator,
            self.binding_registry,
        )
        self.context = InjectionContext(Target(MyType), self.state)
        self.str_context = InjectionContext(Target(str), self.state)
        self.int_context = InjectionContext(Target(int), self.state)

    def test_unknown_binding_type_raises_binding_error(self):
        mock_binding = create_autospec(Binding, spec_set=True)
        self.binding_registry.get_binding.return_value = RegisteredBinding(mock_binding)
        self.binding_registry.__contains__.return_value = True
        with self.assertRaises(BindingError):
            self.provider_factory.create(self.str_context)

    def test_create_with_parent_binding(self):
        self.state.parent_state = InjectionState(create_autospec(ProviderCreator, spec_set=True), self.binding_registry)
        self.binding_registry.__contains__.side_effect = [
            False,
            True,
            False,
        ]

        self.assertTrue(self.provider_factory.create(self.str_context))
        self.assertEqual(
            [
                call(Target(str)),
                call(Target(str)),
                call(Target(str)),
            ],
            self.binding_registry.__contains__.call_args_list,
        )

    def test_create_creates_provider_for_instance_binding(self):
        binding = InstanceBinding(MyType, MyType())
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.provider_factory.create(self.context)
        instance = provider.get()
        self.assertIs(binding.bound_instance, instance)

    def test_create_creates_provider_for_class_binding(self):
        binding = ClassBinding(MyType, OtherType)
        mock_provider = create_autospec(Provider, spec_set=True)
        mock_provider.get.return_value = OtherType()
        self.provider_creator.get_provider.return_value = mock_provider
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.provider_factory.create(self.context)
        instance = provider.get()
        self.assertIsInstance(instance, OtherType)

    def test_create_creates_provider_for_self_binding(self):
        binding = SelfBinding(MyType)
        self.provider_creator.get_provider.return_value = self.mock_scope_provider
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True

        provider = self.provider_factory.create(self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_creates_provider_for_provider_binding(self):
        provider = create_autospec(Provider, spec_set=True)
        provider.get.return_value = MyType()
        binding = ProviderBinding(MyType, provider)
        self.binding_registry.get_binding.return_value = RegisteredBinding(binding)
        self.binding_registry.__contains__.return_value = True
        self.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.provider_factory.create(self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)
