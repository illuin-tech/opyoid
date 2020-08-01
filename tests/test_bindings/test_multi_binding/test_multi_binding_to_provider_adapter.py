import unittest
from unittest.mock import create_autospec

from illuin_inject import ImmediateScope, InstanceBinding, Provider, SingletonScope, ThreadScope
from illuin_inject.bindings import BindingRegistry, MultiBinding, MultiBindingToProviderAdapter
from illuin_inject.bindings.multi_binding import ItemBinding
from illuin_inject.bindings.registered_binding import RegisteredBinding
from illuin_inject.exceptions import BindingError, NonInjectableTypeError
from illuin_inject.injection_state import InjectionState
from illuin_inject.providers import ProviderCreator
from illuin_inject.providers.providers_factories import FromBindingProviderFactory
from illuin_inject.scopes import ThreadScopedProvider


class MyType:
    pass


class TestMultiBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.binding_registry = BindingRegistry()
        self.binding_registry.register(RegisteredBinding(InstanceBinding(SingletonScope, SingletonScope())))
        self.binding_registry.register(RegisteredBinding(InstanceBinding(ThreadScope, ThreadScope())))
        self.adapter = MultiBindingToProviderAdapter(
            FromBindingProviderFactory()
        )
        self.my_instance = MyType()
        self.state = InjectionState(
            ProviderCreator(),
            self.binding_registry,
        )

    def test_create_from_instance_binding(self):
        binding = MultiBinding(MyType, [ItemBinding(bound_instance=self.my_instance)])

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual([self.my_instance], list_instance)

    def test_create_from_class_binding(self):
        binding = MultiBinding(MyType, [ItemBinding(MyType)])

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual(1, len(list_instance))
        self.assertIsInstance(list_instance[0], MyType)

    def test_create_from_provider_binding(self):
        provider = create_autospec(Provider, spec_set=True)
        instance = MyType()
        provider.get.return_value = instance
        binding = MultiBinding(MyType, [ItemBinding(bound_provider=provider)])

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual([instance], list_instance)

    def test_create_without_binding_raises_exception(self):
        binding = MultiBinding(MyType, [ItemBinding()])

        with self.assertRaises(BindingError):
            self.adapter.create(binding, self.state)

    def test_create_scoped_provider(self):
        provider = self.adapter.create(MultiBinding(MyType, [
            ItemBinding(MyType)
        ], scope=ThreadScope), self.state)

        self.assertIsInstance(provider, ThreadScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, list)
        self.assertEqual(1, len(instance))
        self.assertIsInstance(instance[0], MyType)

    def test_non_injectable_scope_raises_exception(self):
        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(MultiBinding(MyType, [], scope=ImmediateScope), self.state)
