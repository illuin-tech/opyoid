import unittest
from unittest.mock import create_autospec

from opyoid import AbstractModule, InstanceBinding, SelfBinding
from opyoid.bindings import InstanceBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter
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
        self.module = create_autospec(AbstractModule, spec_set=True)

    def test_create_returns_provider(self):
        provider = self.adapter.create(
            RegisteredBinding(InstanceBinding(MyType, self.instance), self.module), self.providers_creator
        )

        instance = provider.get()
        self.assertIs(instance, self.instance)

    def test_other_binding_type_raises_exception(self):
        with self.assertRaises(IncompatibleAdapter):
            self.adapter.create(RegisteredBinding(SelfBinding(MyType), self.module), self.providers_creator)
