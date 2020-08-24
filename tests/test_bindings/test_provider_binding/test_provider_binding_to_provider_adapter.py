import unittest
from unittest.mock import call, create_autospec

from opyoid import ClassBinding, InstanceBinding, PerLookupScope, Provider, ProviderBinding, SingletonScope, \
    ThreadScope
from opyoid.bindings import BindingRegistry, FromInstanceProvider, ProviderBindingToProviderAdapter
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.scopes.thread_scoped_provider import ThreadScopedProvider
from opyoid.target import Target


class MyType:
    def __init__(self):
        pass


class TestProviderBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ProviderBindingToProviderAdapter()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.provider = create_autospec(Provider, spec_set=True)
        self.instance = MyType()
        self.provider.get.return_value = self.instance
        self.provider_provider = create_autospec(Provider, spec_set=True)
        self.provider_provider.get.return_value = self.provider
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_accept_provider_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(ProviderBinding(MyType, create_autospec(Provider)), self.state))

    def test_accept_non_provider_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(ClassBinding(MyType), self.state))
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType()), self.state))

    def test_create_returns_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.provider_provider,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ProviderBinding(MyType, Provider), self.state)

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(Provider), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_from_provider_class_binding(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.provider_provider,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ProviderBinding(MyType, Provider), self.state)

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(Provider), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_annotated_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.provider_provider,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(
            ProviderBinding(MyType, Provider, annotation="my_annotation"),
            self.state,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(Provider, "my_annotation"), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_scoped_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.provider_provider,
            FromInstanceProvider(ThreadScope()),
        ]

        provider = self.adapter.create(
            ProviderBinding(MyType, Provider, scope=ThreadScope),
            self.state,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual(
            [
                call(Target(Provider), self.state),
                call(Target(ThreadScope), self.state),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )
        self.assertIsInstance(provider, ThreadScopedProvider)

    def test_non_injectable_scope_raises_exception(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.provider_provider,
            NoBindingFound(),
        ]

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(ProviderBinding(MyType, Provider), self.state)
