import unittest
from unittest.mock import create_autospec

from opyoid import InstanceBinding, Provider, ProviderBinding, SelfBinding
from opyoid.bindings import InstanceBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.injection_context import InjectionContext
from opyoid.providers import ProviderCreator


class MyType:
    pass


class TestInstanceBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = InstanceBindingToProviderAdapter()
        self.providers_creator = create_autospec(ProviderCreator, spec_set=True)
        self.instance = MyType()
        self.context = create_autospec(InjectionContext, spec_set=True)

    def test_accept_instance_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(InstanceBinding(MyType, MyType()), self.context))

    def test_accept_non_instance_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(SelfBinding(MyType), self.context))
        self.assertFalse(self.adapter.accept(ProviderBinding(MyType, create_autospec(Provider)), self.context))

    def test_create_returns_provider(self):
        provider = self.adapter.create(
            RegisteredBinding(InstanceBinding(MyType, self.instance)), self.providers_creator
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)
