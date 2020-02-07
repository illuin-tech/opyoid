import unittest
from typing import Generic, List, Optional, Type, TypeVar

import attr

from illuin_inject import BindingSpec, ClassBinding, PerLookupScope, Injector
from illuin_inject.exceptions import NonInjectableTypeError, NoBindingFound


class MyClass:
    def __init__(self):
        pass


class TestInjector(unittest.TestCase):
    @staticmethod
    def get_injector(*classes_to_bind):
        return Injector(bindings=[
            ClassBinding(class_to_bind)
            for class_to_bind in classes_to_bind
        ])

    def test_simple_injection(self):
        injector = self.get_injector(MyClass)
        my_instance = injector.inject(MyClass)
        self.assertIsInstance(my_instance, MyClass)

    def test_subtype_argument_injection(self):
        class MySubClass(MyClass):
            pass

        class MyOtherClass:
            def __init__(self, my_param: MyClass):
                self.my_param = my_param

        injector = Injector(bindings=[
            ClassBinding(MyClass, MySubClass, PerLookupScope),
            ClassBinding(MyOtherClass),
        ])
        other_instance = injector.inject(MyOtherClass)
        self.assertIsInstance(other_instance.my_param, MyClass)
        self.assertIsInstance(other_instance.my_param, MySubClass)
        my_instance = injector.inject(MyClass)
        self.assertIsInstance(my_instance, MyClass)
        self.assertIsInstance(my_instance, MySubClass)

        with self.assertRaises(NonInjectableTypeError):
            injector.inject(MySubClass)

    def test_unknown_type_injection(self):
        injector = self.get_injector()
        with self.assertRaises(NoBindingFound):
            injector.inject(MyClass)

    def test_unknown_parameter_type_injection(self):
        class MyOtherClass:
            def __init__(self, my_param: MyClass):
                self.my_param = my_param

        class MyLastClass:
            def __init__(self, my_other_param: MyOtherClass):
                self.my_other_param = my_other_param

        with self.assertRaises(NonInjectableTypeError):
            self.get_injector(MyOtherClass, MyLastClass)

    def test_dependency_injection(self):
        class MyParentClass:
            def __init__(self, my_param: MyClass):
                self.my_param = my_param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, MyClass)

    def test_list_injection(self):
        class MyParentClass:
            def __init__(self, param: List[MyClass]):
                self.param = param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, list)
        self.assertEqual(1, len(parent.param))
        self.assertIsInstance(parent.param[0], MyClass)

    def test_list_direct_injection(self):
        class_list = self.get_injector(MyClass).inject(List[MyClass])
        self.assertIsInstance(class_list, list)
        self.assertEqual(1, len(class_list))
        self.assertIsInstance(class_list[0], MyClass)

    def test_optional_injection(self):
        class MyParentClass:
            def __init__(self, param: Optional[MyClass]):
                self.param = param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, MyClass)

    def test_type_direct_injection(self):
        class_type = self.get_injector(MyClass).inject(Type[MyClass])
        self.assertEqual(MyClass, class_type)
        class_type_list = self.get_injector(MyClass).inject(List[Type[MyClass]])
        self.assertEqual([MyClass], class_type_list)

    def test_list_multiple_injection(self):
        class MySubClass(MyClass):
            pass

        class MyParentClass:
            def __init__(self, param: List[MyClass]):
                self.param = param

        my_instance = MyClass()

        class NewBindingSpec(BindingSpec):
            def configure(self) -> None:
                self.bind(MyClass)
                self.bind(MyClass, MySubClass)
                self.bind(MyClass, to_instance=my_instance)
                self.bind(MyParentClass)

        injector = Injector([NewBindingSpec()])
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent.param, list)
        self.assertEqual(3, len(parent.param))
        self.assertIsInstance(parent.param[0], MyClass)
        self.assertIsInstance(parent.param[1], MySubClass)
        self.assertIs(parent.param[2], my_instance)

    def test_attrs_injection(self):
        @attr.s(auto_attribs=True)
        class MyParentClass:
            param: MyClass

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, MyClass)

    def test_attrs_injection_with_factory_default(self):
        @attr.s(auto_attribs=True)
        class MyParentClass:
            param: MyClass = attr.Factory(MyClass)

        parent = self.get_injector(MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent.param, MyClass)

    def test_injector_self_inject(self):
        class MyParentClass:
            def __init__(self, param: Injector):
                self.injector = param

        injector = self.get_injector(MyParentClass)
        parent = injector.inject(MyParentClass)
        self.assertIs(injector, parent.injector)

    def test_inject_type(self):
        class MyOtherClass:
            pass

        class MyParentClass:
            def __init__(self, my_param: Type[MyClass], my_other_param: Type[MyOtherClass]):
                self.my_class = my_param
                self.my_other_class = my_other_param

        parent = self.get_injector(MyClass, MyOtherClass, MyParentClass).inject(MyParentClass)
        self.assertEqual(MyClass, parent.my_class)
        self.assertEqual(MyOtherClass, parent.my_other_class)

    def test_combined_types(self):
        @attr.s(auto_attribs=True)
        class MyParentClass:
            list_type_param: List[Type[MyClass]]
            optional_list_param: Optional[List[MyClass]]
            list_optional_param: List[Optional[MyClass]]
            optional_type_param: Optional[Type[MyClass]]
            optional_list_type_param: Optional[List[Type[MyClass]]]
            list_list_type_param: List[List[Type[MyClass]]]

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertEqual([MyClass], parent.list_type_param)
        self.assertEqual(1, len(parent.optional_list_param))
        self.assertIsInstance(parent.optional_list_param[0], MyClass)
        self.assertEqual(1, len(parent.list_optional_param))
        self.assertIsInstance(parent.list_optional_param[0], MyClass)
        self.assertEqual(MyClass, parent.optional_type_param)
        self.assertEqual([MyClass], parent.optional_list_type_param)
        self.assertEqual([[MyClass]], parent.list_list_type_param)

    def test_list_default(self):
        @attr.s(auto_attribs=True)
        class MyParentClass:
            optional_list_param: Optional[List[MyClass]] = None
            list_param: List[MyClass] = attr.Factory(list)
            list_list_type_param: List[List[Type[MyClass]]] = attr.Factory(list)

        parent = self.get_injector(MyParentClass).inject(MyParentClass)
        self.assertIsNone(parent.optional_list_param)
        self.assertEqual([], parent.list_param)
        self.assertEqual([], parent.list_list_type_param)

    def test_singleton_scope_multiple_bindings(self):
        class MySubType(MyClass):
            pass

        injector = Injector(bindings=[
            ClassBinding(MySubType),
            ClassBinding(MyClass, MySubType),
        ])
        sub_instance_from_sub_type = injector.inject(MySubType)
        sub_instance_from_mother_type = injector.inject(MyClass)

        self.assertIs(sub_instance_from_mother_type, sub_instance_from_sub_type)

    def test_generic_type_parameter_injection(self):
        MyTypeVar = TypeVar("MyTypeVar")

        class MyGeneric(Generic[MyTypeVar]):
            pass

        class MyClass1:
            def __init__(self, my_param: MyGeneric):
                pass

        class MyClass2:
            def __init__(self, my_param: MyGeneric[str]):
                pass

        class MyClass3:
            def __init__(self, my_param: MyGeneric[MyTypeVar]):
                pass

        with self.assertRaises(NonInjectableTypeError):
            Injector(bindings=[
                ClassBinding(MyGeneric),
                ClassBinding(MyClass2),
            ])

        with self.assertRaises(NonInjectableTypeError):
            Injector(bindings=[
                ClassBinding(MyGeneric),
                ClassBinding(MyClass3),
            ])

        injector = self.get_injector(MyGeneric, MyClass1)
        my_generic = injector.inject(MyGeneric)
        self.assertIsInstance(my_generic, MyGeneric)
        my_instance_1 = injector.inject(MyClass1)
        self.assertIsInstance(my_instance_1, MyClass1)
