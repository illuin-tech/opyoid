import unittest
from typing import List

from illuin_inject import BindingSpec, PerLookupScope, SingletonScope
from illuin_inject.bindings import ClassBinding, FactoryBinding, InstanceBinding, MultiBinding
from illuin_inject.bindings.multi_binding import ItemBinding
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.target import Target


class MyType:
    pass


class OtherType(MyType):
    pass


class MyFactory(Factory[MyType]):
    def create(self) -> MyType:
        return MyType()


class TestBindingSpec(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_spec = BindingSpec()
        self.my_instance = MyType()
        self.my_factory = MyFactory()

    def test_configure_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.binding_spec.configure()

    def test_install(self):
        class OtherBindingSpec(BindingSpec):
            def configure(self) -> None:
                self.bind(MyType)
                self.bind(OtherType, annotation="my_annotation")

        binding_spec = OtherBindingSpec()
        self.binding_spec.install(binding_spec)
        self.assertEqual(
            {
                Target(MyType): ClassBinding(MyType),
                Target(OtherType, "my_annotation"): ClassBinding(OtherType, annotation="my_annotation"),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_itself(self):
        self.binding_spec.bind(MyType)

        self.assertEqual(
            {
                Target(MyType): ClassBinding(MyType, MyType),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_another_class(self):
        self.binding_spec.bind(MyType, OtherType)

        self.assertEqual(
            {
                Target(MyType): ClassBinding(MyType, OtherType),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_instance(self):
        my_instance = MyType()
        self.binding_spec.bind(MyType, to_instance=my_instance)

        self.assertEqual(
            {
                Target(MyType): InstanceBinding(MyType, my_instance),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_multiple_overrides_binding(self):
        self.binding_spec.bind(MyType, to_instance=self.my_instance)
        self.binding_spec.bind(MyType, OtherType)

        self.assertEqual(
            {
                Target(MyType): ClassBinding(MyType, OtherType),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_scope(self):
        self.binding_spec.bind(MyType, scope=PerLookupScope)
        self.assertEqual(
            {
                Target(MyType): ClassBinding(MyType, MyType, PerLookupScope),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_annotation(self):
        my_instance = MyType()
        self.binding_spec.bind(MyType, to_instance=my_instance)
        self.binding_spec.bind(MyType, annotation="my_annotation")
        my_other_instance = OtherType()
        self.binding_spec.bind(OtherType, to_instance=my_other_instance, annotation="my_other_annotation")

        self.assertEqual(
            {
                Target(MyType): InstanceBinding(MyType, my_instance),
                Target(MyType, "my_annotation"): ClassBinding(MyType, annotation="my_annotation"),
                Target(OtherType, "my_other_annotation"):
                    InstanceBinding(OtherType, my_other_instance, "my_other_annotation"),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_instance_with_scope_raises_exception(self):
        with self.assertRaises(BindingError):
            self.binding_spec.bind(MyType, to_instance=self.my_instance, scope=PerLookupScope)

    def test_bind_factory_class(self):
        self.binding_spec.bind(MyType, to_factory=MyFactory, scope=PerLookupScope, annotation="my_annotation")
        self.assertEqual(
            {
                Target(MyType, "my_annotation"): FactoryBinding(MyType, MyFactory, PerLookupScope, "my_annotation"),
                Target(MyFactory, "my_annotation"):
                    ClassBinding(MyFactory, scope=PerLookupScope, annotation="my_annotation"),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_factory_instance(self):
        self.binding_spec.bind(MyType, to_factory=self.my_factory)
        self.assertEqual(
            {
                Target(MyType): FactoryBinding(MyType, self.my_factory),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_bind_non_factory_raises_exception(self):
        with self.assertRaises(BindingError):
            self.binding_spec.bind(MyType, to_factory=MyType)

    def test_bind_non_class_raises_exception(self):
        with self.assertRaises(BindingError):
            self.binding_spec.bind(MyType, to_class="hello")

    def test_multi_binding(self):
        instance = MyType()
        self.binding_spec.multi_bind(
            MyType,
            [
                self.binding_spec.bind_item(MyType),
                self.binding_spec.bind_item(to_instance=instance),
            ],
            PerLookupScope,
            "my_annotation",
            False,
        )

        self.assertEqual(
            {
                Target(List[MyType], "my_annotation"): MultiBinding(
                    MyType,
                    [
                        ItemBinding(MyType),
                        ItemBinding(bound_instance=instance),
                    ],
                    PerLookupScope,
                    "my_annotation",
                    False,
                ),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )

    def test_multi_binding_default_parameters(self):
        self.binding_spec.multi_bind(
            MyType,
            [
                self.binding_spec.bind_item(MyType),
            ],
        )

        self.assertEqual(
            {
                Target(List[MyType]): MultiBinding(
                    MyType,
                    [
                        ItemBinding(MyType),
                    ],
                    SingletonScope,
                    None,
                    True,
                ),
            },
            self.binding_spec.binding_registry.get_bindings_by_target()
        )
