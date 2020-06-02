import unittest
from typing import List, Optional, Set, Tuple, Type
from unittest.mock import ANY

from illuin_inject.bindings import BindingRegistry, ClassBinding, FactoryBinding, FromClassProvider, \
    FromInstanceProvider, InstanceBinding
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.providers import ProvidersCreator
from illuin_inject.providers.list_provider import ListProvider
from illuin_inject.scopes.singleton_scoped_provider import SingletonScopedProvider
from illuin_inject.target import Target


class MyType:
    pass


class MyOtherType:
    pass


class TestGraphBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        self.providers_creator = ProvidersCreator(self.binding_registry)
        self.my_instance = MyType()
        self.my_instance_binding = InstanceBinding(MyType, self.my_instance)
        self.annotated_instance = MyType()
        self.my_annotated_instance_binding = InstanceBinding(MyType, self.annotated_instance, "my_annotation")
        self.my_other_instance = MyOtherType()
        self.my_other_instance_binding = InstanceBinding(MyOtherType, self.my_other_instance)

    def test_get_providers_with_instance_bindings(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(self.my_other_instance_binding)

        providers = self.providers_creator.get_providers(Target(MyType))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIsInstance(instance, MyType)

        providers = self.providers_creator.get_providers(Target(MyOtherType))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIsInstance(instance, MyOtherType)

    def test_get_providers_caches_providers(self):
        self.binding_registry.register(self.my_instance_binding)

        providers_1 = self.providers_creator.get_providers(Target(MyType))
        providers_2 = self.providers_creator.get_providers(Target(MyType))
        self.assertIs(providers_1[0], providers_2[0])

    def test_get_providers_with_annotated_bindings(self):
        self.binding_registry.register(self.my_annotated_instance_binding)

        with self.assertRaises(NoBindingFound):
            self.providers_creator.get_providers(Target(MyType))

        providers = self.providers_creator.get_providers(Target(MyType, "my_annotation"))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIs(self.annotated_instance, instance)

    def test_get_multiple_providers_for_type_keeps_order(self):
        my_class_binding = ClassBinding(MyType)
        self.binding_registry.register(my_class_binding)
        self.binding_registry.register(self.my_instance_binding)

        providers = self.providers_creator.get_providers(Target(MyType))
        self.assertEqual(2, len(providers))
        self.assertIsInstance(providers[0], SingletonScopedProvider)
        self.assertIsInstance(providers[1], FromInstanceProvider)

    def test_missing_binding_raises_exception(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(my_parent_class_binding)

        with self.assertRaises(NonInjectableTypeError):
            self.providers_creator.get_providers(Target(MyParentClass))

    def test_list_binding_uses_list_over_item_binding(self):
        list_instance = [self.my_instance]
        list_instance_binding = InstanceBinding(List[MyType], list_instance)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(list_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))

        providers = self.providers_creator.get_providers(Target(List[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        list_instance = providers[0].get()
        self.assertIs(list_instance, list_instance)

    def test_list_binding_without_explicit_binding(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))

        providers = self.providers_creator.get_providers(Target(List[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], ListProvider)
        list_instance = providers[0].get()
        self.assertEqual([self.my_instance, ANY], list_instance)
        self.assertIsInstance(list_instance[1], MyType)

    def test_list_binding_with_annotations(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(self.my_annotated_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))

        providers = self.providers_creator.get_providers(Target(List[MyType], "my_annotation"))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], ListProvider)
        list_instance = providers[0].get()
        self.assertEqual([self.annotated_instance], list_instance)

    def test_set_binding_without_explicit_binding(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))

        providers = self.providers_creator.get_providers(Target(Set[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromClassProvider)
        set_instance = providers[0].get()
        self.assertIn(self.my_instance, set_instance)
        self.assertEqual(2, len(set_instance))

    def test_tuple_binding_without_explicit_binding(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))

        providers = self.providers_creator.get_providers(Target(Tuple[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromClassProvider)
        tuple_instance = providers[0].get()
        self.assertEqual((self.my_instance, ANY), tuple_instance)
        self.assertIsInstance(tuple_instance[1], MyType)

    def test_optional_binding(self):
        self.binding_registry.register(self.my_instance_binding)

        providers = self.providers_creator.get_providers(Target(Optional[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIs(self.my_instance, instance)

    def test_type_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType, SubType))

        providers = self.providers_creator.get_providers(Target(Type[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIs(SubType, instance)

    def test_type_binding_with_explicit_binding(self):
        class SubType(MyType):
            pass

        self.binding_registry.register(InstanceBinding(Type[MyType], MyType))
        self.binding_registry.register(ClassBinding(MyType, SubType))

        providers = self.providers_creator.get_providers(Target(Type[MyType]))
        self.assertEqual(1, len(providers))
        self.assertIsInstance(providers[0], FromInstanceProvider)
        instance = providers[0].get()
        self.assertIs(MyType, instance)

    def test_type_binding_without_class_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Type[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(parent_class_binding)

        with self.assertRaises(NonInjectableTypeError):
            self.providers_creator.get_providers(Target(Type[MyType]))

    def test_factory_binding(self):
        class MyInjectee:
            pass

        class MyFactory(Factory[MyInjectee]):
            def __init__(self, my_param: MyType):
                self.my_param = my_param

            def create(self) -> MyInjectee:
                return MyInjectee()

        factory_binding = FactoryBinding(MyInjectee, MyFactory)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(factory_binding)

        self.providers_creator.get_providers(Target(MyInjectee))
