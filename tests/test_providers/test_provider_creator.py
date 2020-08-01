import unittest
from typing import List, Optional, Set, Tuple, Type
from unittest.mock import ANY

from illuin_inject import Provider
from illuin_inject.bindings import BindingRegistry, ClassBinding, FromClassProvider, FromInstanceProvider, \
    InstanceBinding, ListProvider, MultiBinding, ProviderBinding
from illuin_inject.bindings.multi_binding import ItemBinding
from illuin_inject.bindings.registered_binding import RegisteredBinding
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.injection_state import InjectionState
from illuin_inject.providers import ProviderCreator
from illuin_inject.scopes import SingletonScope
from illuin_inject.target import Target


class MyType:
    pass


class MyOtherType:
    pass


class TestProviderCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        self.binding_registry.register(RegisteredBinding(InstanceBinding(SingletonScope, SingletonScope())))
        self.provider_creator = ProviderCreator()
        self.state = InjectionState(
            self.provider_creator,
            self.binding_registry,
        )
        self.my_instance = MyType()
        self.my_instance_binding = InstanceBinding(MyType, self.my_instance)
        self.annotated_instance = MyType()
        self.my_annotated_instance_binding = InstanceBinding(MyType, self.annotated_instance, "my_annotation")
        self.my_other_instance = MyOtherType()
        self.my_other_instance_binding = InstanceBinding(MyOtherType, self.my_other_instance)

    def test_get_provider_with_instance_bindings(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(self.my_other_instance_binding))

        provider = self.provider_creator.get_provider(Target(MyType), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

        provider = self.provider_creator.get_provider(Target(MyOtherType), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)

    def test_get_provider_caches_providers(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))

        provider_1 = self.provider_creator.get_provider(Target(MyType), self.state)
        provider_2 = self.provider_creator.get_provider(Target(MyType), self.state)
        self.assertIs(provider_1, provider_2)

    def test_get_provider_with_annotated_bindings(self):
        self.binding_registry.register(RegisteredBinding(self.my_annotated_instance_binding))

        with self.assertRaises(NoBindingFound):
            self.provider_creator.get_provider(Target(MyType), self.state)

        provider = self.provider_creator.get_provider(Target(MyType, "my_annotation"), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(self.annotated_instance, instance)

    def test_missing_binding_raises_exception(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(RegisteredBinding(my_parent_class_binding))

        with self.assertRaises(NonInjectableTypeError):
            self.provider_creator.get_provider(Target(MyParentClass), self.state)

    def test_list_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(MyType),
                    ],
                )
            )
        )

        provider = self.provider_creator.get_provider(Target(List[MyType]), self.state)
        list_instance = provider.get()
        self.assertEqual([self.my_instance, ANY], list_instance)
        self.assertIsInstance(list_instance[1], MyType)

    def test_list_binding_with_annotations(self):
        self.binding_registry.register(
            RegisteredBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.annotated_instance),
                    ],
                    annotation="my_annotation",
                )
            )
        )
        self.binding_registry.register(
            RegisteredBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                    ],
                )
            )
        )
        self.binding_registry.register(RegisteredBinding(self.my_annotated_instance_binding))
        self.binding_registry.register(RegisteredBinding(ClassBinding(MyType)))

        provider = self.provider_creator.get_provider(Target(List[MyType], "my_annotation"), self.state)
        list_instance = provider.get()
        self.assertEqual([self.annotated_instance], list_instance)

    def test_set_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(MyType),
                    ],
                )
            )
        )
        provider = self.provider_creator.get_provider(Target(Set[MyType]), self.state)
        self.assertIsInstance(provider, FromClassProvider)
        set_instance = provider.get()
        self.assertIn(self.my_instance, set_instance)
        self.assertEqual(2, len(set_instance))

    def test_tuple_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(MyType),
                    ],
                )
            )
        )
        provider = self.provider_creator.get_provider(Target(Tuple[MyType]), self.state)
        self.assertIsInstance(provider, FromClassProvider)
        tuple_instance = provider.get()
        self.assertEqual((self.my_instance, ANY), tuple_instance)
        self.assertIsInstance(tuple_instance[1], MyType)

    def test_optional_binding(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))

        provider = self.provider_creator.get_provider(Target(Optional[MyType]), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(self.my_instance, instance)

    def test_type_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(ClassBinding(MyType, SubType)))

        provider = self.provider_creator.get_provider(Target(Type[MyType]), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(SubType, instance)

    def test_type_binding_with_explicit_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(RegisteredBinding(InstanceBinding(Type[MyType], MyType)))
        self.binding_registry.register(RegisteredBinding(ClassBinding(MyType, SubType)))

        provider = self.provider_creator.get_provider(Target(Type[MyType]), self.state)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(MyType, instance)

    def test_type_binding_without_class_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Type[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(parent_class_binding))

        with self.assertRaises(NonInjectableTypeError):
            self.provider_creator.get_provider(Target(Type[MyType]), self.state)

    def test_provider_binding(self):
        class MyInjectee:
            pass

        class MyProvider(Provider[MyInjectee]):
            def __init__(self, my_param: MyType):
                self.my_param = my_param

            def get(self) -> MyInjectee:
                return MyInjectee()

        provider_binding = ProviderBinding(MyInjectee, MyProvider)
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(provider_binding))

        self.provider_creator.get_provider(Target(MyInjectee), self.state)

    def test_list_implicit_binding(self):
        instance = MyType()
        self.binding_registry.register(RegisteredBinding(InstanceBinding(MyType, instance)))
        provider = self.provider_creator.get_provider(Target(List[MyType]), self.state)
        self.assertIsInstance(provider, ListProvider)
        list_instance = provider.get()
        self.assertEqual([instance], list_instance)
