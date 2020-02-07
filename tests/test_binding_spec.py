import unittest

from illuin_inject import BindingSpec, PerLookupScope
from illuin_inject.bindings import ClassBinding, InstanceBinding
from illuin_inject.exceptions import BindingError


class MyType:
    pass


class OtherType(MyType):
    pass


class TestBindingSpec(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_spec = BindingSpec()
        self.my_instance = MyType()

    def test_configure_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.binding_spec.configure()

    def test_install(self):
        class OtherBindingSpec(BindingSpec):
            def configure(self) -> None:
                self.bind(MyType)

        binding_spec = OtherBindingSpec()
        self.binding_spec.install(binding_spec)
        self.assertEqual(
            {
                MyType: [ClassBinding(MyType)]
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_class_to_itself(self):
        self.binding_spec.bind(MyType)

        self.assertEqual(
            {
                MyType: [ClassBinding(MyType, MyType)],
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_class_to_another_class(self):
        self.binding_spec.bind(MyType, OtherType)

        self.assertEqual(
            {
                MyType: [ClassBinding(MyType, OtherType)],
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_instance(self):
        my_instance = MyType()
        self.binding_spec.bind(MyType, to_instance=my_instance)

        self.assertEqual(
            {
                MyType: [InstanceBinding(MyType, my_instance)],
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_multiple(self):
        self.binding_spec.bind(MyType, to_instance=self.my_instance)
        self.binding_spec.bind(MyType, OtherType)

        self.assertEqual(
            {
                MyType: [InstanceBinding(MyType, self.my_instance), ClassBinding(MyType, OtherType)],
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_with_scope(self):
        self.binding_spec.bind(MyType, scope=PerLookupScope)
        self.assertEqual(
            {
                MyType: [ClassBinding(MyType, MyType, PerLookupScope)],
            },
            self.binding_spec.binding_registry.get_bindings_by_target_type()
        )

    def test_bind_class_and_instance_raises_exception(self):
        with self.assertRaises(BindingError):
            self.binding_spec.bind(MyType, MyType, to_instance=self.my_instance)

    def test_bind_instance_with_scope_raises_exception(self):
        with self.assertRaises(BindingError):
            self.binding_spec.bind(MyType, to_instance=self.my_instance, scope=PerLookupScope)
