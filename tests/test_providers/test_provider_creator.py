import unittest
from typing import List, Optional, Set, Tuple, Type
from unittest.mock import ANY

from opyoid import Provider, SelfBinding
from opyoid.bindings import (
    BindingRegistry,
    ClassBinding,
    FromCallableProvider,
    FromInstanceProvider,
    InstanceBinding,
    ListProvider,
    MultiBinding,
    ProviderBinding,
)
from opyoid.bindings.multi_binding import ItemBinding
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.bindings.registered_multi_binding import RegisteredMultiBinding
from opyoid.exceptions import NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.scopes import SingletonScope
from opyoid.target import Target


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
        self.context = InjectionContext(Target(MyType), self.state)
        self.other_context = InjectionContext(Target(MyOtherType), self.state)
        self.named_context = InjectionContext(Target(MyType, "my_name"), self.state)
        self.my_instance = MyType()
        self.my_instance_binding = InstanceBinding(MyType, self.my_instance)
        self.named_instance = MyType()
        self.my_named_instance_binding = InstanceBinding(MyType, self.named_instance, named="my_name")
        self.my_other_instance = MyOtherType()
        self.my_other_instance_binding = InstanceBinding(MyOtherType, self.my_other_instance)

    def test_get_provider_with_instance_bindings(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(self.my_other_instance_binding))

        provider = self.provider_creator.get_provider(self.context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

        provider = self.provider_creator.get_provider(self.other_context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)

    def test_get_provider_caches_providers(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))

        provider_1 = self.provider_creator.get_provider(self.context)
        provider_2 = self.provider_creator.get_provider(self.context)
        self.assertIs(provider_1, provider_2)

    def test_get_provider_with_named_bindings(self):
        self.binding_registry.register(RegisteredBinding(self.my_named_instance_binding))

        with self.assertRaises(NoBindingFound):
            self.provider_creator.get_provider(self.context)

        provider = self.provider_creator.get_provider(self.named_context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(self.named_instance, instance)

    def test_missing_binding_raises_exception(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_binding = SelfBinding(MyParentClass)
        context = InjectionContext(Target(MyParentClass), self.state)
        self.binding_registry.register(RegisteredBinding(my_parent_binding))

        with self.assertRaises(NonInjectableTypeError):
            self.provider_creator.get_provider(context)

    def test_list_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredMultiBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(bound_class=MyType),
                    ],
                ),
                item_bindings=[
                    RegisteredBinding(InstanceBinding(MyType, self.my_instance)),
                    RegisteredBinding(SelfBinding(MyType)),
                ],
            )
        )
        context = InjectionContext(Target(List[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        list_instance = provider.get()
        self.assertEqual([self.my_instance, ANY], list_instance)
        self.assertIsInstance(list_instance[1], MyType)

    def test_list_binding_with_named_arguments(self):
        self.binding_registry.register(
            RegisteredMultiBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.named_instance),
                    ],
                    named="my_name",
                ),
                item_bindings=[RegisteredBinding(InstanceBinding(MyType, self.named_instance, named="my_name"))],
            )
        )
        self.binding_registry.register(
            RegisteredMultiBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                    ],
                ),
                item_bindings=[RegisteredBinding(InstanceBinding(MyType, self.my_instance))],
            )
        )
        self.binding_registry.register(RegisteredBinding(self.my_named_instance_binding))
        self.binding_registry.register(RegisteredBinding(SelfBinding(MyType)))

        context = InjectionContext(Target(List[MyType], "my_name"), self.state)
        provider = self.provider_creator.get_provider(context)
        list_instance = provider.get()
        self.assertEqual([self.named_instance], list_instance)

    def test_set_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredMultiBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(bound_class=MyType),
                    ],
                ),
                item_bindings=[
                    RegisteredBinding(InstanceBinding(MyType, self.my_instance)),
                    RegisteredBinding(SelfBinding(MyType)),
                ],
            )
        )
        context = InjectionContext(Target(Set[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, FromCallableProvider)
        set_instance = provider.get()
        self.assertIn(self.my_instance, set_instance)
        self.assertEqual(2, len(set_instance))

    def test_tuple_binding_with_multi_binding(self):
        self.binding_registry.register(
            RegisteredMultiBinding(
                MultiBinding(
                    MyType,
                    [
                        ItemBinding(bound_instance=self.my_instance),
                        ItemBinding(bound_class=MyType),
                    ],
                ),
                item_bindings=[
                    RegisteredBinding(InstanceBinding(MyType, self.my_instance)),
                    RegisteredBinding(SelfBinding(MyType)),
                ],
            )
        )
        context = InjectionContext(Target(Tuple[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, FromCallableProvider)
        tuple_instance = provider.get()
        self.assertEqual((self.my_instance, ANY), tuple_instance)
        self.assertIsInstance(tuple_instance[1], MyType)

    def test_optional_binding(self):
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))

        context = InjectionContext(Target(Optional[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(self.my_instance, instance)

    def test_type_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(ClassBinding(MyType, SubType)))

        context = InjectionContext(Target(Type[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(SubType, instance)

    def test_type_binding_with_explicit_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(RegisteredBinding(InstanceBinding(Type[MyType], MyType)))
        self.binding_registry.register(RegisteredBinding(ClassBinding(MyType, SubType)))

        context = InjectionContext(Target(Type[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, FromInstanceProvider)
        instance = provider.get()
        self.assertIs(MyType, instance)

    def test_type_binding_without_class_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Type[MyType]):
                self.my_param = my_param

        parent_binding = SelfBinding(MyParentClass)
        self.binding_registry.register(RegisteredBinding(self.my_instance_binding))
        self.binding_registry.register(RegisteredBinding(parent_binding))
        context = InjectionContext(Target(Type[MyType]), self.state)

        with self.assertRaises(NonInjectableTypeError):
            self.provider_creator.get_provider(context)

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
        context = InjectionContext(Target(MyInjectee), self.state)

        self.provider_creator.get_provider(context)

    def test_list_implicit_binding(self):
        instance = MyType()
        self.binding_registry.register(RegisteredBinding(InstanceBinding(MyType, instance)))
        context = InjectionContext(Target(List[MyType]), self.state)
        provider = self.provider_creator.get_provider(context)
        self.assertIsInstance(provider, ListProvider)
        list_instance = provider.get()
        self.assertEqual([instance], list_instance)
