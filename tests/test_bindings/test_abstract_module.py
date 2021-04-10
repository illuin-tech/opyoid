import unittest
from typing import List

from opyoid import AbstractModule, Module, PerLookupScope, Provider, SelfBinding, SingletonScope
from opyoid.bindings import ClassBinding, InstanceBinding, MultiBinding, ProviderBinding
from opyoid.bindings.multi_binding import ItemBinding
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.bindings.registered_multi_binding import RegisteredMultiBinding
from opyoid.exceptions import BindingError
from opyoid.frozen_target import FrozenTarget


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
                self.bind(OtherType, named="my_name")

        module = OtherModule()
        self.module.install(module)
        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(SelfBinding(MyType)),
                FrozenTarget(OtherType, "my_name"): RegisteredBinding(
                    SelfBinding(OtherType, named="my_name")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_itself(self):
        self.module.bind(MyType)

        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(SelfBinding(MyType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_class_to_another_class(self):
        self.module.bind(MyType, to_class=OtherType)

        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(ClassBinding(MyType, OtherType)),
                FrozenTarget(OtherType): RegisteredBinding(SelfBinding(OtherType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_instance(self):
        my_instance = MyType()
        self.module.bind(MyType, to_instance=my_instance)

        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(InstanceBinding(MyType, my_instance)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_multiple_overrides_binding(self):
        self.module.bind(MyType, to_instance=self.my_instance)
        self.module.bind(MyType, to_class=OtherType)

        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(ClassBinding(MyType, OtherType)),
                FrozenTarget(OtherType): RegisteredBinding(SelfBinding(OtherType)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_scope(self):
        self.module.bind(MyType, scope=PerLookupScope)
        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(SelfBinding(MyType, scope=PerLookupScope)),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_with_name(self):
        my_instance = MyType()
        self.module.bind(MyType, to_instance=my_instance)
        self.module.bind(MyType, named="my_name")
        my_other_instance = OtherType()
        self.module.bind(OtherType, to_instance=my_other_instance, named="my_other_name")

        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(InstanceBinding(MyType, my_instance)),
                FrozenTarget(MyType, "my_name"): RegisteredBinding(
                    SelfBinding(MyType, named="my_name")),
                FrozenTarget(OtherType, "my_other_name"):
                    RegisteredBinding(InstanceBinding(OtherType, my_other_instance, named="my_other_name")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_provider_class(self):
        self.module.bind(MyType, to_provider=MyProvider, scope=PerLookupScope, named="my_name")
        self.assertEqual(
            {
                FrozenTarget(MyType, "my_name"): RegisteredBinding(
                    ProviderBinding(MyType, MyProvider, scope=PerLookupScope, named="my_name")),
                FrozenTarget(MyProvider, "my_name"): RegisteredBinding(
                    SelfBinding(MyProvider, scope=PerLookupScope, named="my_name")),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_bind_provider_instance(self):
        self.module.bind(MyType, to_provider=self.my_provider)
        self.assertEqual(
            {
                FrozenTarget(MyType): RegisteredBinding(ProviderBinding(MyType, self.my_provider)),
                FrozenTarget(MyProvider): RegisteredBinding(InstanceBinding(MyProvider, self.my_provider)),
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
        provider = MyProvider
        self.module.multi_bind(
            MyType,
            [
                self.module.bind_item(to_class=MyType),
                self.module.bind_item(to_instance=instance),
                self.module.bind_item(to_provider=provider),
            ],
            scope=PerLookupScope,
            named="my_name",
            override_bindings=False,
        )

        self.assertEqual(
            {
                FrozenTarget(List[MyType], "my_name"): RegisteredMultiBinding(
                    MultiBinding(
                        MyType,
                        [
                            ItemBinding(bound_class=MyType),
                            ItemBinding(bound_instance=instance),
                            ItemBinding(bound_provider=provider),
                        ],
                        scope=PerLookupScope,
                        named="my_name",
                        override_bindings=False,
                    ),
                    item_bindings=[
                        RegisteredBinding(
                            SelfBinding(MyType, scope=PerLookupScope, named="my_name"),
                        ),
                        RegisteredBinding(
                            InstanceBinding(MyType, instance, named="my_name"),
                        ),
                        RegisteredBinding(
                            ProviderBinding(MyType, provider, scope=PerLookupScope, named="my_name"),
                        )
                    ]
                ),
                FrozenTarget(MyProvider, "my_name"): RegisteredBinding(
                    SelfBinding(MyProvider, scope=PerLookupScope, named="my_name")
                ),
                FrozenTarget(MyType, "my_name"): RegisteredBinding(
                    InstanceBinding(MyType, instance, named="my_name")
                )
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_multi_binding_default_parameters(self):
        self.module.multi_bind(
            MyType,
            [
                self.module.bind_item(to_class=MyType),
            ],
        )

        self.assertEqual(
            {
                FrozenTarget(List[MyType]): RegisteredMultiBinding(
                    MultiBinding(
                        MyType,
                        [
                            ItemBinding(bound_class=MyType),
                        ],
                        scope=SingletonScope,
                        named=None,
                        override_bindings=True,
                    ),
                    item_bindings=[
                        RegisteredBinding(
                            SelfBinding(MyType),
                        )
                    ]
                ),
            },
            self.module.binding_registry.get_bindings_by_target()
        )

    def test_multi_binding_with_empty_item_raises_exception(self):
        with self.assertRaises(BindingError):
            self.module.multi_bind(
                MyType,
                [
                    self.module.bind_item(),
                ],
            )
