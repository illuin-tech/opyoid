import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, PerLookupScope, SingletonScope, ThreadScope
from illuin_inject.bindings import BindingRegistry, FactoryBindingToProviderAdapter, FromInstanceProvider
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.injection_state import InjectionState
from illuin_inject.provider import Provider
from illuin_inject.providers import ProviderCreator
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider
from illuin_inject.target import Target


class MyType:
    def __init__(self):
        pass


class TestFactoryBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = FactoryBindingToProviderAdapter()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.factory = create_autospec(Factory, spec_set=True)
        self.instance = MyType()
        self.factory.create.return_value = self.instance
        self.factory_provider = create_autospec(Provider, spec_set=True)
        self.factory_provider.get.return_value = self.factory
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_accept_factory_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(FactoryBinding(MyType, create_autospec(Factory)), self.state))

    def test_accept_non_factory_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(ClassBinding(MyType), self.state))
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType()), self.state))

    def test_create_returns_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(FactoryBinding(MyType, self.factory), self.state)

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_from_factory_class_binding(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.factory_provider,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(FactoryBinding(MyType, Factory), self.state)

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(Factory), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_annotated_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(
            FactoryBinding(MyType, self.factory, annotation="my_annotation"),
            self.state,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual([
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_scoped_provider(self):
        self.state.provider_creator.get_provider.side_effect = [
            self.factory_provider,
            FromInstanceProvider(ThreadScope()),
        ]

        provider = self.adapter.create(
            FactoryBinding(MyType, Factory, scope=ThreadScope),
            self.state,
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
        self.assertEqual(
            [
                call(Target(Factory), self.state),
                call(Target(ThreadScope), self.state),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )
        self.assertIsInstance(provider, ThreadScopedProvider)

    def test_non_injectable_scope_raises_exception(self):
        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound(),
        ]

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(FactoryBinding(MyType, self.factory), self.state)
