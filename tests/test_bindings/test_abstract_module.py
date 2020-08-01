import unittest
from typing import List

from illuin_inject import AbstractModule, Module, PerLookupScope, Provider, SelfBinding, SingletonScope
from illuin_inject.bindings import ClassBinding, InstanceBinding, MultiBinding, ProviderBinding
from illuin_inject.bindings.multi_binding import ItemBinding
from illuin_inject.bindings.registered_binding import RegisteredBinding
from illuin_inject.exceptions import BindingError
from illuin_inject.target import Target


class MyType:
    pass


class OtherType(MyType):
    pass


class MyProvider(Provider[MyType]):
    def get(self) -> MyType:
        return MyType()


class TestAbstractModule(unittest.TestCase):
    def setUp(self) -> None:
        self.module = AbstractModule()
        self.my_instance = MyType()
        self.my_provider = MyProvider()

    def test_configure_is_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.module.configure()

    def test_configure_once_runs_once(self):
        with self.assertRaises(NotImplementedError):
            self.module.configure_once()

        self.module.configure_once()

    def test_install(self):
        class OtherModule(Module):
            def configure(self) -> None:
                self.bind(MyType)
                self.bind(OtherType, annotation="my_annotation")

        module = OtherModule()
        self.module.install(module)
        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(SelfBinding(MyType)),
                Target(OtherType, "my_annotation"): RegisteredBinding(
                    SelfBinding(OtherType, annotation="my_annotation")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_itself(self):
        self.module.bind(MyType)

        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(SelfBinding(MyType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_another_class(self):
        self.module.bind(MyType, OtherType)

        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(ClassBinding(MyType, OtherType)),
                Target(OtherType): RegisteredBinding(SelfBinding(OtherType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_instance(self):
        my_instance = MyType()
        self.module.bind(MyType, to_instance=my_instance)

        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(InstanceBinding(MyType, my_instance)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_multiple_overrides_binding(self):
        self.module.bind(MyType, to_instance=self.my_instance)
        self.module.bind(MyType, OtherType)

        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(ClassBinding(MyType, OtherType)),
                Target(OtherType): RegisteredBinding(SelfBinding(OtherType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_scope(self):
        self.module.bind(MyType, scope=PerLookupScope)
        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(SelfBinding(MyType, PerLookupScope)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_annotation(self):
        my_instance = MyType()
        self.module.bind(MyType, to_instance=my_instance)
        self.module.bind(MyType, annotation="my_annotation")
        my_other_instance = OtherType()
        self.module.bind(OtherType, to_instance=my_other_instance, annotation="my_other_annotation")

        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(InstanceBinding(MyType, my_instance)),
                Target(MyType, "my_annotation"): RegisteredBinding(SelfBinding(MyType, annotation="my_annotation")),
                Target(OtherType, "my_other_annotation"):
                    RegisteredBinding(InstanceBinding(OtherType, my_other_instance, "my_other_annotation")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_provider_class(self):
        self.module.bind(MyType, to_provider=MyProvider, scope=PerLookupScope, annotation="my_annotation")
        self.assertEqual(
            {
                Target(MyType, "my_annotation"): RegisteredBinding(
                    ProviderBinding(MyType, MyProvider, PerLookupScope, "my_annotation")),
                Target(MyProvider, "my_annotation"): RegisteredBinding(
                    SelfBinding(MyProvider, scope=PerLookupScope, annotation="my_annotation")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_factory_instance(self):
        self.module.bind(MyType, to_provider=self.my_provider)
        self.assertEqual(
            {
                Target(MyType): RegisteredBinding(ProviderBinding(MyType, self.my_provider)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_non_provider_raises_exception(self):
        with self.assertRaises(BindingError):
            self.module.bind(MyType, to_provider=MyType)

    def test_bind_non_class_raises_exception(self):
        with self.assertRaises(BindingError):
            self.module.bind(MyType, to_class="hello")

    def test_multi_binding(self):
        instance = MyType()
        self.module.multi_bind(
            MyType,
            [
                self.module.bind_item(MyType),
                self.module.bind_item(to_instance=instance),
            ],
            PerLookupScope,
            "my_annotation",
            False,
        )

        self.assertEqual(
            {
                Target(List[MyType], "my_annotation"): RegisteredBinding(
                    MultiBinding(
                        MyType,
                        [
                            ItemBinding(MyType),
                            ItemBinding(bound_instance=instance),
                        ],
                        PerLookupScope,
                        "my_annotation",
                        False,
                    )
                ),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_multi_binding_default_parameters(self):
        self.module.multi_bind(
            MyType,
            [
                self.module.bind_item(MyType),
            ],
        )

        self.assertEqual(
            {
                Target(List[MyType]): RegisteredBinding(
                    MultiBinding(
                        MyType,
                        [
                            ItemBinding(MyType),
                        ],
                        SingletonScope,
                        None,
                        True,
                    )
                ),
            },
            self.module.binding_registry.get_bindings_by_target()
        )
