import unittest
from unittest.mock import create_autospec

from opyoid import ImmediateScope, InstanceBinding, Provider, ProviderBinding, SelfBinding, SingletonScope, ThreadScope
from opyoid.bindings import BindingRegistry, MultiBinding, MultiBindingToProviderAdapter
from opyoid.bindings.multi_binding import ItemBinding
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.bindings.registered_multi_binding import RegisteredMultiBinding
from opyoid.exceptions import NonInjectableTypeError
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.providers.providers_factories.from_registered_binding_provider_factory import \
    FromRegisteredBindingProviderFactory
from opyoid.scopes import ThreadScopedProvider


class MyType:
    pass


class TestMultiBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.binding_registry = BindingRegistry()
        self.binding_registry.register(RegisteredBinding(InstanceBinding(SingletonScope, SingletonScope())))
        self.binding_registry.register(RegisteredBinding(InstanceBinding(ThreadScope, ThreadScope())))
        self.adapter = MultiBindingToProviderAdapter(
            FromRegisteredBindingProviderFactory()
        )
        self.my_instance = MyType()
        self.state = InjectionState(
            ProviderCreator(),
            self.binding_registry,
        )

    def test_create_from_instance_binding(self):
        binding = RegisteredMultiBinding(
            MultiBinding(MyType, [ItemBinding(bound_instance=self.my_instance)]),
            item_bindings=[
                RegisteredBinding(InstanceBinding(MyType, self.my_instance))
            ]
        )

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual([self.my_instance], list_instance)

    def test_create_from_class_binding(self):
        binding = RegisteredMultiBinding(MultiBinding(MyType, [ItemBinding(MyType)]), item_bindings=[
            RegisteredBinding(SelfBinding(MyType))
        ])

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual(1, len(list_instance))
        self.assertIsInstance(list_instance[0], MyType)

    def test_create_from_provider_binding(self):
        provider = create_autospec(Provider, spec_set=True)
        instance = MyType()
        provider.get.return_value = instance
        binding = RegisteredMultiBinding(MultiBinding(MyType, [ItemBinding(bound_provider=provider)]), item_bindings=[
            RegisteredBinding(ProviderBinding(MyType, provider))
        ])

        provider = self.adapter.create(binding, self.state)

        list_instance = provider.get()
        self.assertEqual([instance], list_instance)

    def test_create_scoped_provider(self):
        provider = self.adapter.create(RegisteredMultiBinding(
            MultiBinding(MyType, [ItemBinding(MyType)], scope=ThreadScope),
            item_bindings=[
                RegisteredBinding(SelfBinding(MyType, scope=ThreadScope))
            ]
        ), self.state)

        self.assertIsInstance(provider, ThreadScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, list)
        self.assertEqual(1, len(instance))
        self.assertIsInstance(instance[0], MyType)

    def test_non_injectable_scope_raises_exception(self):
        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(RegisteredMultiBinding(MultiBinding(MyType, [], scope=ImmediateScope)), self.state)
