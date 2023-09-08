import unittest
from typing import cast, List
from unittest.mock import create_autospec

from opyoid import ClassBinding, PerLookupScope, Provider, SelfBinding
from opyoid.bindings import Binding, BindingRegistry, InstanceBinding, ItemBinding, MultiBinding, ProviderBinding
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.bindings.registered_multi_binding import RegisteredMultiBinding
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
        mock_named_binding = create_autospec(Binding, spec_set=True)
        mock_named_binding.target = FrozenTarget(MyType, "my_name")
        self.my_type_named_binding = RegisteredBinding(mock_named_binding)
        self.my_type_binding_2 = RegisteredBinding(InstanceBinding(MyType, MyType()))
        other_mock_binding = create_autospec(Binding, spec_set=True)
        other_mock_binding.target = FrozenTarget(OtherType)
        self.other_type_binding = RegisteredBinding(other_mock_binding)

    def test_register_saves_binding_to_new_type(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_named_binding)
        self.binding_registry.register(self.other_type_binding)
        self.assertEqual(
            {
                FrozenTarget(MyType): self.my_type_binding,
                FrozenTarget(MyType, "my_name"): self.my_type_named_binding,
                FrozenTarget(OtherType): self.other_type_binding,
            },
            self.binding_registry.get_bindings_by_target(),
        )

    def test_register_multi_binding_saves_binding_to_known_type_in_order(self):
        item_binding_1 = ItemBinding(bound_class=MyType)
        registered_item_binding_1 = RegisteredBinding(SelfBinding(MyType))
        item_binding_2 = ItemBinding(bound_instance=MyType())
        registered_item_binding_2 = RegisteredBinding(InstanceBinding(MyType, item_binding_2.bound_instance))
        binding_1 = RegisteredMultiBinding(
            MultiBinding(MyType, [item_binding_1]),
            item_bindings=[
                registered_item_binding_1,
            ],
        )
        binding_2 = RegisteredMultiBinding(
            MultiBinding(MyType, [item_binding_2], override_bindings=False),
            item_bindings=[
                registered_item_binding_2,
            ],
        )
        self.binding_registry.register(binding_1)
        self.binding_registry.register(binding_2)
        registered_binding = cast(
            RegisteredMultiBinding[MyType], self.binding_registry.get_binding(Target(List[MyType]))
        )
        self.assertIsInstance(registered_binding, RegisteredMultiBinding)
        self.assertIsInstance(registered_binding.raw_binding, MultiBinding)
        self.assertEqual([registered_item_binding_1, registered_item_binding_2], registered_binding.item_bindings)

    def test_register_multi_binding_with_override(self):
        item_binding_1 = ItemBinding(bound_class=MyType)
        item_binding_2 = ItemBinding(bound_instance=MyType())
        binding_1 = RegisteredMultiBinding(MultiBinding(MyType, [item_binding_1]))
        binding_2 = RegisteredMultiBinding(MultiBinding(MyType, [item_binding_2], override_bindings=True))
        self.binding_registry.register(binding_1)
        self.binding_registry.register(binding_2)
        binding = self.binding_registry.get_binding(Target(List[MyType]))
        self.assertIs(binding_2, binding)

    def test_get_binding_returns_binding(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_named_binding)
        self.binding_registry.register(self.my_type_binding_2)
        binding = self.binding_registry.get_binding(Target(MyType))

        self.assertEqual(self.my_type_binding_2, binding)

    def test_get_binding_returns_named_binding(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_named_binding)
        self.binding_registry.register(self.my_type_binding_2)
        binding = self.binding_registry.get_binding(Target(MyType, "my_name"))

        self.assertEqual(self.my_type_named_binding, binding)

    def test_get_binding_for_unknown_type_returns_none(self):
        binding = self.binding_registry.get_binding(Target(MyType))

        self.assertIsNone(binding)

    def test_get_binding_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.other_type_binding)
        binding = self.binding_registry.get_binding(Target("MyType"))

        self.assertEqual(self.my_type_binding, binding)

    def test_get_named_binding_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_named_binding)
        self.binding_registry.register(self.other_type_binding)
        binding = self.binding_registry.get_binding(Target("MyType", "my_name"))

        self.assertEqual(self.my_type_named_binding, binding)

    def test_get_binding_from_unknown_string(self):
        binding = self.binding_registry.get_binding(Target("MyUnknownType"))
        self.assertIsNone(binding)

    def test_get_binding_from_string_with_name_conflict_raises_exception(self):
        class MyNewType:
            pass

        binding_1 = create_autospec(Binding, spec_set=True)
        binding_1.target = FrozenTarget(MyNewType)

        # pylint: disable=function-redefined
        class MyNewType:  # type: ignore[no-redef]
            pass

        binding_2 = create_autospec(Binding, spec_set=True)
        binding_2.target = FrozenTarget(MyNewType)

        self.binding_registry.register(RegisteredBinding(binding_1))
        self.binding_registry.register(RegisteredBinding(binding_2))

        with self.assertRaises(NonInjectableTypeError):
            self.binding_registry.get_binding(Target("MyNewType"))

    def test_register_provider_binding_with_instance_creates_additional_binding(self):
        class MyProvider(Provider[str]):
            def get(self) -> str:
                return "hello"

        provider_instance = MyProvider()
        provider_binding = RegisteredBinding(ProviderBinding(str, provider_instance, named="my_name"))
        self.binding_registry.register(provider_binding)

        self.assertEqual(
            {
                FrozenTarget(str, "my_name"): provider_binding,
                FrozenTarget(MyProvider, "my_name"): RegisteredBinding(
                    InstanceBinding(MyProvider, provider_instance, named="my_name")
                ),
            },
            self.binding_registry.get_bindings_by_target(),
        )

    def test_register_provider_binding_with_class_creates_self_binding(self):
        class MyProvider(Provider[str]):
            def get(self) -> str:
                return "hello"

        provider_binding = RegisteredBinding(ProviderBinding(str, MyProvider, scope=PerLookupScope, named="my_name"))
        self.binding_registry.register(provider_binding)

        self.assertEqual(provider_binding, self.binding_registry.get_binding(Target(str, "my_name")))
        registered_binding = cast(
            RegisteredBinding[str], self.binding_registry.get_binding(Target(MyProvider, "my_name"))
        )
        raw_binding = cast(SelfBinding[str], registered_binding.raw_binding)
        self.assertIsInstance(raw_binding, SelfBinding)
        self.assertEqual(MyProvider, raw_binding.target_type)
        self.assertEqual(PerLookupScope, raw_binding.scope)

    def test_register_multi_binding_with_provider_binding_creates_self_binding(self):
        class MyProvider(Provider[str]):
            def get(self) -> str:
                return "hello"

        provider_binding = RegisteredBinding(ProviderBinding(str, MyProvider))
        multi_binding = RegisteredMultiBinding(
            MultiBinding(str, [ItemBinding(bound_provider=MyProvider)]), item_bindings=[provider_binding]
        )
        self.binding_registry.register(multi_binding)

        registered_binding = cast(RegisteredBinding[str], self.binding_registry.get_binding(Target(MyProvider)))
        self.assertIsInstance(registered_binding.raw_binding, SelfBinding)
        self.assertEqual(MyProvider, registered_binding.raw_binding.target_type)

    def test_register_class_binding_creates_self_binding_if_target_does_not_exist(self):
        class MySubType(MyType):
            pass

        class_binding = RegisteredBinding(ClassBinding(MyType, MySubType))
        self.binding_registry.register(class_binding)
        self.assertIs(class_binding, self.binding_registry.get_binding(Target(MyType)))
        self_binding = cast(RegisteredBinding[MySubType], self.binding_registry.get_binding(Target(MySubType)))
        self.assertIsInstance(self_binding.raw_binding, SelfBinding)
        self.assertEqual(MySubType, self_binding.raw_binding.target_type)

    def test_register_class_binding_does_not_create_self_binding_if_target_exists(self):
        class MySubType(MyType):
            pass

        my_instance = MySubType()
        class_binding = RegisteredBinding(ClassBinding(MyType, MySubType))
        instance_binding = RegisteredBinding(InstanceBinding(MySubType, my_instance))
        self.binding_registry.register(instance_binding)
        self.binding_registry.register(class_binding)
        self.assertIs(class_binding, self.binding_registry.get_binding(Target(MyType)))
        self.assertIs(instance_binding, self.binding_registry.get_binding(Target(MySubType)))
