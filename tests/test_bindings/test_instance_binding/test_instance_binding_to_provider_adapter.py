import unittest
from unittest.mock import create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding
from illuin_inject.bindings import BindingRegistry, InstanceBindingToProviderAdapter
from illuin_inject.factory import Factory
from illuin_inject.injection_state import InjectionState
from illuin_inject.providers import ProviderCreator


class MyType:
    def __init__(self):
        pass


class TestInstanceBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = InstanceBindingToProviderAdapter()
        self.providers_creator = create_autospec(ProviderCreator, spec_set=True)
        self.instance = MyType()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )

    def test_accept_instance_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(InstanceBinding(MyType, MyType()), self.state))

    def test_accept_non_instance_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(ClassBinding(MyType), self.state))
        self.assertFalse(self.adapter.accept(FactoryBinding(MyType, create_autospec(Factory)), self.state))

    def test_create_returns_provider(self):
        provider = self.adapter.create(InstanceBinding(MyType, self.instance), self.providers_creator)

        instance = provider.get()
        self.assertIs(instance, self.instance)
