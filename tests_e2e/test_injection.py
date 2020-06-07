import unittest
from typing import Generic, List, Optional, Set, Tuple, Type, TypeVar

import attr

from illuin_inject import ClassBinding, Provider, ProviderBinding, ImmediateScope, Injector, InstanceBinding, \
    ItemBinding, \
    Module, MultiBinding, PerLookupScope, annotated_arg
from illuin_inject.bindings.private_module import PrivateModule
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.injector_options import InjectorOptions


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

    def test_auto_injection(self):
        class ParentClass:
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        injector = Injector(options=InjectorOptions(auto_bindings=True))
        my_instance = injector.inject(ParentClass)
        self.assertIsInstance(my_instance, ParentClass)
        self.assertIsInstance(my_instance.my_arg, MyClass)

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

        parent = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(MyClass)]), ClassBinding(MyParentClass)]
        ).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, list)
        self.assertEqual(1, len(parent.param))
        self.assertIsInstance(parent.param[0], MyClass)

    def test_set_direct_injection(self):
        class_set = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(MyClass)])]
        ).inject(Set[MyClass])
        self.assertIsInstance(class_set, set)
        self.assertEqual(1, len(list(class_set)))
        self.assertIsInstance(class_set.pop(), MyClass)

    def test_set_injection(self):
        class MyParentClass:
            def __init__(self, param: Set[MyClass]):
                self.param = param

        parent = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(MyClass)]), ClassBinding(MyParentClass)]
        ).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, set)
        self.assertEqual(1, len(list(parent.param)))
        self.assertIsInstance(parent.param.pop(), MyClass)

    def test_list_direct_injection(self):
        class_list = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(MyClass)])]
        ).inject(List[MyClass])
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

        class NewModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(MyClass),
                        self.bind_item(MySubClass),
                        self.bind_item(to_instance=my_instance),
                    ],
                )
                self.bind(MyParentClass)

        injector = Injector([NewModule()])
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

    def test_singleton_scope_multiple_modules(self):
        class MyOtherClass:
            pass

        class MyCompositeClass(MyClass, MyOtherClass):
            pass

        class Module1(Module):
            def configure(self) -> None:
                self.bind(MyClass, MyCompositeClass)

        class Module2(Module):
            def configure(self) -> None:
                self.bind(MyOtherClass, MyCompositeClass)

        injector = Injector([
            Module1(),
            Module2(),
        ])
        instance_1 = injector.inject(MyClass)
        instance_2 = injector.inject(MyOtherClass)
        self.assertIs(instance_1, instance_2)

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

    def test_annotated_arg(self):
        class Class1:
            @annotated_arg("my_param", "type_1")
            @annotated_arg("my_other_param", "type_2")
            def __init__(self, my_param: str, my_other_param: str, my_default_param: str):
                self.my_param = my_param
                self.my_other_param = my_other_param
                self.my_default_param = my_default_param

        injector = Injector(bindings=[
            InstanceBinding(str, "my_type_1", "type_1"),
            InstanceBinding(str, "my_type_2", "type_2"),
            InstanceBinding(str, "my_default"),
            ClassBinding(Class1),
        ])
        instance = injector.inject(Class1)
        self.assertIsInstance(instance, Class1)
        self.assertEqual("my_type_1", instance.my_param)
        self.assertEqual("my_type_2", instance.my_other_param)
        self.assertEqual("my_default", instance.my_default_param)

    def test_annotated_list(self):
        class Class1:
            @annotated_arg("my_param", "type_1")
            @annotated_arg("my_other_param", "type_2")
            def __init__(self, my_param: List[str], my_other_param: List[str], my_default_param: List[str]):
                self.my_param = my_param
                self.my_other_param = my_other_param
                self.my_default_param = my_default_param

        injector = Injector(bindings=[
            ClassBinding(Class1),
            MultiBinding(
                str,
                [
                    ItemBinding(bound_instance="my_type_1"),
                ],
                annotation="type_1"
            ),
            MultiBinding(
                str,
                [
                    ItemBinding(bound_instance="my_type_2"),
                ],
                annotation="type_2"
            ),
            MultiBinding(
                str,
                [
                    ItemBinding(bound_instance="my_default"),
                ],
            ),
        ])
        instance = injector.inject(Class1)
        self.assertIsInstance(instance, Class1)
        self.assertEqual(["my_type_1"], instance.my_param)
        self.assertEqual(["my_type_2"], instance.my_other_param)
        self.assertEqual(["my_default"], instance.my_default_param)

    def test_immediate_injection(self):
        called = []

        class MyOtherClass:
            def __init__(self):
                called.append("ok")

        Injector(bindings=[
            ClassBinding(MyOtherClass, scope=ImmediateScope),
        ])

        self.assertEqual(["ok"], called)

    def test_from_provider_injection(self):
        class MyParent:
            def __init__(self, my_arg: MyClass, my_str: str):
                self.my_arg = my_arg
                self.my_str = my_str

        class MyParentProvider(Provider[MyParent]):
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

            def get(self) -> MyParent:
                return MyParent(self.my_arg, "hello")

        injector = Injector(bindings=[
            ClassBinding(MyClass),
            ProviderBinding(MyParent, MyParentProvider),
        ])
        my_parent = injector.inject(MyParent)
        self.assertIsInstance(my_parent.my_arg, MyClass)
        self.assertEqual("hello", my_parent.my_str)

    def test_provider_injection_with_provider_binding(self):
        class MyParent:
            def __init__(self, my_arg: MyClass, my_str: str):
                self.my_arg = my_arg
                self.my_str = my_str

        class MyParentProvider(Provider[MyParent]):
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

            def get(self) -> MyParent:
                return MyParent(self.my_arg, "hello")

        injector = Injector(bindings=[
            InstanceBinding(MyParentProvider, MyParentProvider(MyClass())),
            ProviderBinding(MyParent, MyParentProvider),
        ])
        my_parent = injector.inject(MyParent)
        self.assertIsInstance(my_parent.my_arg, MyClass)
        self.assertEqual("hello", my_parent.my_str)

    def test_provider_instance_injection(self):
        class MyParent:
            def __init__(self, my_arg: MyClass, my_str: str):
                self.my_arg = my_arg
                self.my_str = my_str

        class MyParentProvider(Provider[MyParent]):
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

            def get(self) -> MyParent:
                return MyParent(self.my_arg, "hello")

        injector = Injector(bindings=[
            ProviderBinding(MyParent, MyParentProvider(MyClass())),
        ])
        my_parent = injector.inject(MyParent)
        self.assertIsInstance(my_parent.my_arg, MyClass)
        self.assertEqual("hello", my_parent.my_str)

    def test_shared_singleton(self):
        class MyParentA:
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        class MyParentB:
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        injector = Injector(bindings=[
            ClassBinding(MyClass),
            ClassBinding(MyParentA),
            ClassBinding(MyParentB),
        ])
        my_parent_a = injector.inject(MyParentA)
        my_parent_b = injector.inject(MyParentB)

        self.assertIs(my_parent_a.my_arg, my_parent_b.my_arg)

    def test_annotated_singleton(self):
        class MyParentA:
            @annotated_arg("my_arg", "annotation_1")
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        class MyParentB:
            @annotated_arg("my_arg", "annotation_2")
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        injector = Injector(bindings=[
            ClassBinding(MyClass, annotation="annotation_1"),
            ClassBinding(MyClass, annotation="annotation_2"),
            ClassBinding(MyParentA),
            ClassBinding(MyParentB),
        ])
        my_parent_a = injector.inject(MyParentA)
        my_parent_b = injector.inject(MyParentB)

        self.assertIsNot(my_parent_a.my_arg, my_parent_b.my_arg)

    def test_inject_list_with_singleton_items(self):
        class SubClass1(MyClass):
            pass

        class SubClass2(MyClass):
            pass

        injector = Injector(bindings=[MultiBinding(MyClass, [ItemBinding(SubClass1), ItemBinding(SubClass2)])])
        list_1 = injector.inject(List[MyClass])
        list_2 = injector.inject(List[MyClass])

        self.assertEqual(2, len(list_1))
        self.assertEqual(2, len(list_2))
        self.assertIsInstance(list_1[0], SubClass1)
        self.assertIs(list_1[0], list_2[0])
        self.assertIsInstance(list_1[1], SubClass2)
        self.assertIs(list_1[1], list_2[1])

    def test_list_injection_item_singletons(self):
        injector = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(MyClass)])]
        )
        list_instance = injector.inject(List[MyClass])
        tuple_instance = injector.inject(Tuple[MyClass])
        self.assertIs(list_instance[0], tuple_instance[0])

    def test_private_module_does_not_expose_bindings(self):
        instance_1 = MyClass()

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.bind(MyClass, to_instance=instance_1)

        injector = Injector([MyPrivateModule()])
        with self.assertRaises(NonInjectableTypeError):
            injector.inject(MyClass)

    def test_private_module_uses_exposed_bindings(self):
        instance_1 = MyClass()

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(
                    self.bind(MyClass, to_instance=instance_1)
                )

        injector = Injector([MyPrivateModule()])
        instance = injector.inject(MyClass)
        self.assertIs(instance_1, instance)

    def test_private_module_use_private_binding_through_exposed_binding(self):
        class MyParentClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(
                    self.bind(MyParentClass)
                )
                self.bind(MyClass)

        injector = Injector([MyPrivateModule()])
        instance = injector.inject(MyParentClass)
        self.assertIsInstance(instance, MyParentClass)
        self.assertIsInstance(instance.arg, MyClass)

    def test_private_module_uses_public_binding_through_private_binding(self):
        class MyParentClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(
                    self.bind(MyParentClass)
                )

        injector = Injector([MyPrivateModule()], [ClassBinding(MyClass)])
        parent = injector.inject(MyParentClass)
        child = injector.inject(MyClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.arg, MyClass)
        self.assertIs(parent.arg, child)

    def test_private_module_reuses_state(self):
        class MyParentClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(
                    self.bind(MyParentClass),
                    self.bind(MyClass),
                )

        injector = Injector([MyPrivateModule()])
        parent = injector.inject(MyParentClass)
        child = injector.inject(MyClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(child, MyClass)
        self.assertIs(parent.arg, child)

    def test_provider_injection(self):
        class MyParentClass:
            def __init__(self, my_param: Provider[MyClass]):
                self.my_param = my_param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, Provider)
        instance = parent.my_param.get()
        self.assertIsInstance(instance, MyClass)

    def test_provider_injection_from_provider_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Provider[MyClass]):
                self.my_param = my_param

        class MyProvider(Provider[MyClass]):
            def get(self) -> MyClass:
                return MyClass()

        provider = MyProvider()
        injector = Injector(bindings=[ProviderBinding(MyClass, provider), ClassBinding(MyParentClass)])
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIs(parent.my_param, provider)
        instance = parent.my_param.get()
        self.assertIsInstance(instance, MyClass)
