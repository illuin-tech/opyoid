import unittest
from typing import List
from unittest.mock import create_autospec, patch

from illuin_inject import ClassBinding, PerLookupScope
from illuin_inject.bindings import Binding, BindingRegistry, FactoryBinding, InstanceBinding, MultiBinding
from illuin_inject.bindings.multi_binding import ItemBinding
from illuin_inject.bindings.registered_binding import RegisteredBinding
from illuin_inject.factory import Factory
from illuin_inject.target import Target


class MyType:
    pass


class OtherType:
    pass


class TestBindingRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        mock_binding = create_autospec(Binding, spec_set=True)
        mock_binding.target = Target(MyType)
        self.my_type_binding = RegisteredBinding(mock_binding)
        mock_annotated_binding = create_autospec(Binding, spec_set=True)
        mock_annotated_binding.target = Target(MyType, "my_annotation")
        self.my_type_annotated_binding = RegisteredBinding(mock_annotated_binding)
        self.my_type_binding_2 = RegisteredBinding(InstanceBinding(MyType, MyType()))
        other_mock_binding = create_autospec(Binding, spec_set=True)
        other_mock_binding.target = Target(OtherType)
        self.other_type_binding = RegisteredBinding(other_mock_binding)

    def test_register_saves_binding_to_new_type(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.other_type_binding)
        self.assertEqual({
            Target(MyType): self.my_type_binding,
            Target(MyType, "my_annotation"): self.my_type_annotated_binding,
            Target(OtherType): self.other_type_binding,
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

    def test_update(self):
        binding_registry = BindingRegistry()
        binding_registry.register(self.my_type_binding_2)
        binding_registry.register(self.other_type_binding)
        self.binding_registry.register(self.my_type_binding)

        self.binding_registry.update(binding_registry)
        self.assertEqual({
            Target(MyType): self.my_type_binding_2,
            Target(OtherType): self.other_type_binding,
        }, self.binding_registry.get_bindings_by_target())

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

    def test_get_binding_from_string_with_name_conflict(self):
        class MyNewType:
            pass

        binding_1 = create_autospec(Binding, spec_set=True)
        binding_1.target = Target(MyNewType)

        # pylint: disable=function-redefined
        class MyNewType:
            pass

        binding_2 = create_autospec(Binding, spec_set=True)
        binding_2.target = Target(MyNewType)

        self.binding_registry.register(RegisteredBinding(binding_1))
        self.binding_registry.register(RegisteredBinding(binding_2))

        with patch("logging.Logger.error") as mock_error:
            binding = self.binding_registry.get_binding(Target("MyNewType"))
        self.assertIsNone(binding)
        mock_error.assert_called_once_with(
            "Could not find binding for 'MyNewType': multiple types with this name found")

    def test_register_factory_binding_does_not_create_additional_binding(self):
        class MyFactory(Factory[str]):
            def create(self) -> str:
                return "hello"

        factory_instance = MyFactory()
        factory_binding = RegisteredBinding(FactoryBinding(str, factory_instance, annotation="my_annotation"))
        self.binding_registry.register(factory_binding)

        self.assertEqual(
            {
                Target(str, "my_annotation"): factory_binding,
            },
            self.binding_registry.get_bindings_by_target()
        )

    def test_register_factory_binding_creates_class_binding(self):
        class MyFactory(Factory[str]):
            def create(self) -> str:
                return "hello"

        factory_binding = RegisteredBinding(FactoryBinding(str, MyFactory, PerLookupScope, "my_annotation"))
        self.binding_registry.register(factory_binding)

        self.assertEqual(factory_binding, self.binding_registry.get_binding(Target(str, "my_annotation")))
        factory_binding = self.binding_registry.get_binding(Target(MyFactory, "my_annotation"))
        self.assertIsInstance(factory_binding.raw_binding, ClassBinding)
        self.assertEqual(MyFactory, factory_binding.raw_binding.target_type)
        self.assertEqual(PerLookupScope, factory_binding.raw_binding.scope)
        self.assertEqual(MyFactory, factory_binding.raw_binding.bound_type)
