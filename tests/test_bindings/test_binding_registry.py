import unittest
from typing import List
from unittest.mock import create_autospec

from opyoid import PerLookupScope, Provider, SelfBinding
from opyoid.bindings import Binding, BindingRegistry, InstanceBinding, ItemBinding, MultiBinding, ProviderBinding
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import NonInjectableTypeError
from opyoid.frozen_target import FrozenTarget
from opyoid.target import Target


class MyType:
    pass


class OtherType:
    pass


class TestBindingRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        mock_binding = create_autospec(Binding, spec_set=True)
        mock_binding.target = FrozenTarget(MyType)
        self.my_type_binding = RegisteredBinding(mock_binding)
        mock_annotated_binding = create_autospec(Binding, spec_set=True)
        mock_annotated_binding.target = FrozenTarget(MyType, "my_annotation")
        self.my_type_annotated_binding = RegisteredBinding(mock_annotated_binding)
        self.my_type_binding_2 = RegisteredBinding(InstanceBinding(MyType, MyType()))
        other_mock_binding = create_autospec(Binding, spec_set=True)
        other_mock_binding.target = FrozenTarget(OtherType)
        self.other_type_binding = RegisteredBinding(other_mock_binding)

    def test_register_saves_binding_to_new_type(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.other_type_binding)
        self.assertEqual({
            FrozenTarget(MyType): self.my_type_binding,
            FrozenTarget(MyType, "my_annotation"): self.my_type_annotated_binding,
            FrozenTarget(OtherType): self.other_type_binding,
        }, self.binding_registry.get_bindings_by_target())

    def test_register_multi_binding_saves_binding_to_known_type_in_order(self):
        item_binding_1 = ItemBinding(MyType)
        item_binding_2 = ItemBinding(bound_instance=MyType())
        binding_1 = RegisteredBinding(MultiBinding(MyType, [item_binding_1]))
        binding_2 = RegisteredBinding(MultiBinding(MyType, [item_binding_2], override_bindings=False))
        self.binding_registry.register(binding_1)
        self.binding_registry.register(binding_2)
        binding = self.binding_registry.get_binding(Target(List[MyType])).raw_binding
        self.assertIsInstance(binding, MultiBinding)
        self.assertEqual([item_binding_1, item_binding_2], binding.item_bindings)

    def test_register_multi_binding_with_override(self):
        item_binding_1 = ItemBinding(MyType)
        item_binding_2 = ItemBinding(bound_instance=MyType())
        binding_1 = RegisteredBinding(MultiBinding(MyType, [item_binding_1]))
        binding_2 = RegisteredBinding(MultiBinding(MyType, [item_binding_2], override_bindings=True))
        self.binding_registry.register(binding_1)
        self.binding_registry.register(binding_2)
        binding = self.binding_registry.get_binding(Target(List[MyType])).raw_binding
        self.assertIsInstance(binding, MultiBinding)
        self.assertEqual([item_binding_2], binding.item_bindings)

    def test_get_binding_returns_binding(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.my_type_binding_2)
        binding = self.binding_registry.get_binding(Target(MyType))

        self.assertEqual(self.my_type_binding_2, binding)

    def test_get_binding_returns_annotated_binding(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.my_type_binding_2)
        binding = self.binding_registry.get_binding(Target(MyType, "my_annotation"))

        self.assertEqual(self.my_type_annotated_binding, binding)

    def test_get_binding_for_unknown_type_returns_none(self):
        binding = self.binding_registry.get_binding(Target(MyType))

        self.assertIsNone(binding)

    def test_get_binding_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.other_type_binding)
        binding = self.binding_registry.get_binding(Target("MyType"))

        self.assertEqual(self.my_type_binding, binding)

    def test_get_annotated_binding_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.other_type_binding)
        binding = self.binding_registry.get_binding(Target("MyType", "my_annotation"))

        self.assertEqual(self.my_type_annotated_binding, binding)

    def test_get_binding_from_unknown_string(self):
        binding = self.binding_registry.get_binding(Target("MyUnknownType"))
        self.assertIsNone(binding)

    def test_get_binding_from_string_with_name_conflict_raises_exception(self):
        class MyNewType:
            pass

        binding_1 = create_autospec(Binding, spec_set=True)
        binding_1.target = FrozenTarget(MyNewType)

        # pylint: disable=function-redefined
        class MyNewType:
            pass

        binding_2 = create_autospec(Binding, spec_set=True)
        binding_2.target = FrozenTarget(MyNewType)

        self.binding_registry.register(RegisteredBinding(binding_1))
        self.binding_registry.register(RegisteredBinding(binding_2))

        with self.assertRaises(NonInjectableTypeError):
            self.binding_registry.get_binding(Target("MyNewType"))

    def test_register_provider_binding_with_instance_does_not_create_additional_binding(self):
        class MyProvider(Provider[str]):
            def get(self) -> str:
                return "hello"

        provider_instance = MyProvider()
        provider_binding = RegisteredBinding(ProviderBinding(str, provider_instance, annotation="my_annotation"))
        self.binding_registry.register(provider_binding)

        self.assertEqual(
            {
                FrozenTarget(str, "my_annotation"): provider_binding,
            },
            self.binding_registry.get_bindings_by_target()
        )

    def test_register_provider_binding_with_class_creates_self_binding(self):
        class MyProvider(Provider[str]):
            def get(self) -> str:
                return "hello"

        provider_binding = RegisteredBinding(ProviderBinding(str, MyProvider, PerLookupScope, "my_annotation"))
        self.binding_registry.register(provider_binding)

        self.assertEqual(provider_binding, self.binding_registry.get_binding(Target(str, "my_annotation")))
        provider_binding = self.binding_registry.get_binding(Target(MyProvider, "my_annotation"))
        self.assertIsInstance(provider_binding.raw_binding, SelfBinding)
        self.assertEqual(MyProvider, provider_binding.raw_binding.target_type)
        self.assertEqual(PerLookupScope, provider_binding.raw_binding.scope)
