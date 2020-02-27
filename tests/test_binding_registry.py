import unittest
from unittest.mock import patch

from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import Binding, InstanceBinding
from illuin_inject.target import Target


class MyType:
    pass


class OtherType:
    pass


class TestBindingRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        self.my_type_binding = Binding(MyType)
        self.my_type_annotated_binding = Binding(MyType, "my_annotation")
        self.my_type_binding_2 = InstanceBinding(MyType, MyType())
        self.other_type_binding = Binding(OtherType)

    def test_register_saves_binding_to_new_type(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.other_type_binding)
        self.assertEqual({
            Target(MyType): [self.my_type_binding],
            Target(MyType, "my_annotation"): [self.my_type_annotated_binding],
            Target(OtherType): [self.other_type_binding],
        }, self.binding_registry.get_bindings_by_target())

    def test_register_saves_binding_to_known_type_in_order(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_binding_2)
        self.assertEqual({
            Target(MyType): [self.my_type_binding, self.my_type_binding_2],
        }, self.binding_registry.get_bindings_by_target())

    def test_update(self):
        binding_registry = BindingRegistry()
        binding_registry.register(self.my_type_binding_2)
        binding_registry.register(self.other_type_binding)
        self.binding_registry.register(self.my_type_binding)

        self.binding_registry.update(binding_registry)
        self.assertEqual({
            Target(MyType): [self.my_type_binding, self.my_type_binding_2],
            Target(OtherType): [self.other_type_binding]
        }, self.binding_registry.get_bindings_by_target())

    def test_get_bindings_returns_bindings(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.my_type_binding_2)
        bindings = self.binding_registry.get_bindings(Target(MyType))

        self.assertEqual([self.my_type_binding, self.my_type_binding_2], bindings)

    def test_get_bindings_returns_annotated_bindings(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.my_type_binding_2)
        bindings = self.binding_registry.get_bindings(Target(MyType, "my_annotation"))

        self.assertEqual([self.my_type_annotated_binding], bindings)

    def test_get_bindings_for_unknown_type_returns_empty_list(self):
        bindings = self.binding_registry.get_bindings(Target(MyType))

        self.assertEqual([], bindings)

    def test_get_bindings_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.other_type_binding)
        bindings = self.binding_registry.get_bindings(Target("MyType"))

        self.assertEqual([self.my_type_binding], bindings)

    def test_get_annotated_bindings_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_annotated_binding)
        self.binding_registry.register(self.other_type_binding)
        bindings = self.binding_registry.get_bindings(Target("MyType", "my_annotation"))

        self.assertEqual([self.my_type_annotated_binding], bindings)

    def test_get_bindings_from_unknown_string(self):
        bindings = self.binding_registry.get_bindings(Target("MyUnknownType"))
        self.assertEqual([], bindings)

    def test_get_bindings_from_string_with_name_conflict(self):
        class MyNewType:
            pass

        type_1 = MyNewType

        # pylint: disable=function-redefined
        class MyNewType:
            pass

        type_2 = MyNewType

        self.binding_registry.register(Binding(type_1))
        self.binding_registry.register(Binding(type_2))

        with patch("logging.Logger.error") as mock_error:
            bindings = self.binding_registry.get_bindings(Target("MyNewType"))
        self.assertEqual([], bindings)
        mock_error.assert_called_once_with(
            "Could not find binding for 'MyNewType': multiple types with this name found")
