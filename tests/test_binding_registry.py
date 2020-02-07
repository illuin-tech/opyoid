import unittest
from unittest.mock import patch

from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import Binding, InstanceBinding


class MyType:
    pass


class OtherType:
    pass


class TestBindingRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        self.my_type_binding = Binding(MyType)
        self.my_type_binding_2 = InstanceBinding(MyType, MyType())
        self.other_type_binding = Binding(OtherType)

    def test_register_saves_binding_to_new_type(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.other_type_binding)
        self.assertEqual({
            MyType: [self.my_type_binding],
            OtherType: [self.other_type_binding],
        }, self.binding_registry.get_bindings_by_target_type())

    def test_register_saves_binding_to_known_type_in_order(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_binding_2)
        self.assertEqual({
            MyType: [self.my_type_binding, self.my_type_binding_2],
        }, self.binding_registry.get_bindings_by_target_type())

    def test_update(self):
        binding_registry = BindingRegistry()
        binding_registry.register(self.my_type_binding_2)
        binding_registry.register(self.other_type_binding)
        self.binding_registry.register(self.my_type_binding)

        self.binding_registry.update(binding_registry)
        self.assertEqual({
            MyType: [self.my_type_binding, self.my_type_binding_2],
            OtherType: [self.other_type_binding]
        }, self.binding_registry.get_bindings_by_target_type())

    def test_get_bindings_returns_bindings(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.my_type_binding_2)
        bindings = self.binding_registry.get_bindings(MyType)

        self.assertEqual([self.my_type_binding, self.my_type_binding_2], bindings)

    def test_get_bindings_for_unknown_type_returns_empty_list(self):
        bindings = self.binding_registry.get_bindings(MyType)

        self.assertEqual([], bindings)

    def test_get_bindings_from_string(self):
        self.binding_registry.register(self.my_type_binding)
        self.binding_registry.register(self.other_type_binding)
        bindings = self.binding_registry.get_bindings("MyType")

        self.assertEqual([self.my_type_binding], bindings)

    def test_get_bindings_from_unknown_string(self):
        bindings = self.binding_registry.get_bindings("MyUnknownType")
        self.assertEqual([], bindings)

    def test_get_bindings_from_string_with_name_conflict(self):
        # noinspection PyGlobalUndefined
        # pylint: disable=redefined-outer-name, global-variable-undefined, invalid-name
        global MyType

        type_1 = MyType

        class MyType:
            pass

        type_2 = MyType

        self.binding_registry.register(Binding(type_1))
        self.binding_registry.register(Binding(type_2))

        with patch("logging.Logger.error") as mock_error:
            bindings = self.binding_registry.get_bindings("MyType")
        self.assertEqual([], bindings)
        mock_error.assert_called_once_with("Could not find binding for 'MyType': multiple types with this name found")
