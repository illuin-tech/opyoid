import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding
from illuin_inject.bindings import Binding, BindingRegistry, FromInstanceProvider
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.providers import ProvidersCreator
from illuin_inject.providers.providers_factories import FromBindingsProvidersFactory
from illuin_inject.target import Target


class MyType:
    pass


class TestFromBindingsProvidersFactory(unittest.TestCase):
    def setUp(self):
        self.binding_registry = create_autospec(BindingRegistry, spec_set=True)
        self.providers_factory = FromBindingsProvidersFactory(
            self.binding_registry,
        )
        self.providers_creator = create_autospec(ProvidersCreator, spec_set=True)

    def test_unknown_binding_type_raises_binding_error(self):
        self.binding_registry.get_bindings.return_value = [
            Binding()
        ]
        with self.assertRaises(BindingError):
            self.providers_factory.create(Target(str), self.providers_creator)

    def test_accept(self):
        self.binding_registry.get_bindings.side_effect = [
            [create_autospec(Binding, spec_set=True)],
            [],
        ]

        self.assertTrue(self.providers_factory.accept(Target(str)))
        self.assertFalse(self.providers_factory.accept(Target(int)))
        self.assertEqual(
            [
                call(Target(str)),
                call(Target(int)),
            ],
            self.binding_registry.get_bindings.call_args_list
        )

    def test_create_creates_provider_for_instance_binding(self):
        binding = InstanceBinding(MyType, MyType())
        self.binding_registry.get_bindings.return_value = [binding]

        providers = self.providers_factory.create(Target(MyType), self.providers_creator)
        self.assertEqual(1, len(providers))
        instance = providers[0].get()
        self.assertIs(binding.bound_instance, instance)

    def test_create_creates_provider_for_class_binding(self):
        binding = ClassBinding(MyType)
        self.binding_registry.get_bindings.return_value = [binding]

        providers = self.providers_factory.create(Target(MyType), self.providers_creator)
        self.assertEqual(1, len(providers))
        instance = providers[0].get()
        self.assertIsInstance(instance, MyType)

    def test_create_creates_provider_for_factory_binding(self):
        factory = create_autospec(Factory, spec_set=True)
        factory.create.return_value = MyType()
        binding = FactoryBinding(MyType, factory)
        self.binding_registry.get_bindings.return_value = [binding]
        self.providers_creator.get_providers.return_value = [FromInstanceProvider(factory)]

        providers = self.providers_factory.create(Target(MyType), self.providers_creator)
        self.assertEqual(1, len(providers))
        instance = providers[0].get()
        self.assertIsInstance(instance, MyType)
