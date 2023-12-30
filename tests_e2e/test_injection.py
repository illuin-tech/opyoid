import os
import unittest
from typing import cast, Generic, List, Optional, Set, Tuple, Type, TypeVar, Union

import attr

from opyoid import (
    ClassBinding,
    ImmediateScope,
    Injector,
    InstanceBinding,
    ItemBinding,
    Module,
    MultiBinding,
    named_arg,
    PerLookupScope,
    Provider,
    ProviderBinding,
    SelfBinding,
    SingletonScope,
)
from opyoid.bindings.private_module import PrivateModule
from opyoid.exceptions import CyclicDependencyError, NoBindingFound, NonInjectableTypeError
from opyoid.injector_options import InjectorOptions
from opyoid.scopes.context_scope import ContextScope


class MyClass:
    pass


class TestInjector(unittest.TestCase):
    @staticmethod
    def get_injector(*classes_to_bind) -> Injector:
        return Injector(bindings=[SelfBinding(class_to_bind) for class_to_bind in classes_to_bind])

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

    def test_auto_injection_with_default(self):
        class ParentClass:
            def __init__(self, my_arg: str = "default"):
                self.my_arg = my_arg

        injector = Injector(options=InjectorOptions(auto_bindings=True))
        my_instance = injector.inject(ParentClass)
        self.assertIsInstance(my_instance, ParentClass)
        self.assertEqual("default", my_instance.my_arg)

    def test_auto_injection_with_named_binding(self):
        class ParentClass:
            @named_arg("my_arg", "my_name")
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        injector = Injector(options=InjectorOptions(auto_bindings=True))
        my_instance = injector.inject(ParentClass)
        self.assertIsInstance(my_instance, ParentClass)
        self.assertIsInstance(my_instance.my_arg, MyClass)

    def test_auto_injection_with_binding_override(self):
        class ParentClass:
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        class MySubClass(MyClass):
            pass

        injector = Injector(
            bindings=[ClassBinding(MyClass, MySubClass)],
            options=InjectorOptions(auto_bindings=True),
        )
        my_instance = injector.inject(ParentClass)
        self.assertIsInstance(my_instance, ParentClass)
        self.assertIsInstance(my_instance.my_arg, MySubClass)

    def test_subtype_argument_injection(self):
        class MySubClass(MyClass):
            pass

        class MyOtherClass:
            def __init__(self, my_param: MyClass):
                self.my_param = my_param

        injector = Injector(
            bindings=[
                ClassBinding(MyClass, MySubClass, scope=PerLookupScope),
                SelfBinding(MyOtherClass),
            ]
        )
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
            bindings=[
                MultiBinding(MyClass, [ItemBinding(bound_class=MyClass)]),
                SelfBinding(MyParentClass),
            ]
        ).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, list)
        self.assertEqual(1, len(parent.param))
        self.assertIsInstance(parent.param[0], MyClass)

    def test_set_direct_injection(self):
        class_set = Injector(bindings=[MultiBinding(MyClass, [ItemBinding(bound_class=MyClass)])]).inject(Set[MyClass])
        self.assertIsInstance(class_set, set)
        self.assertEqual(1, len(list(class_set)))
        self.assertIsInstance(class_set.pop(), MyClass)

    def test_set_injection(self):
        class MyParentClass:
            def __init__(self, param: Set[MyClass]):
                self.param = param

        parent = Injector(
            bindings=[
                MultiBinding(MyClass, [ItemBinding(bound_class=MyClass)]),
                SelfBinding(MyParentClass),
            ]
        ).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, set)
        self.assertEqual(1, len(list(parent.param)))
        self.assertIsInstance(parent.param.pop(), MyClass)

    def test_list_direct_injection(self):
        class_list = Injector(bindings=[MultiBinding(MyClass, [ItemBinding(bound_class=MyClass)])]).inject(
            List[MyClass]
        )
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

    def test_union_injection(self):
        class MyParentClass:
            def __init__(self, param: Union[str, MyClass]):
                self.param = param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, MyClass)

    def test_list_union_injection(self):
        class MyParentClass:
            def __init__(self, params: List[Union[str, int]]):
                self.params = params

        injector = Injector(
            bindings=[
                SelfBinding(MyParentClass),
                InstanceBinding(str, "hello"),
                InstanceBinding(int, 1),
            ]
        )
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertEqual(["hello", 1], parent.params)

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
        my_instance_2 = MyClass()
        my_instance_3 = MyClass()

        class MyProvider(Provider[MyClass]):
            def get(self) -> MyClass:
                return my_instance_2

        class MyProvider2(Provider[MyClass]):
            def get(self) -> MyClass:
                return my_instance_3

        class NewModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    cast(
                        List[ItemBinding[MyClass]],
                        [
                            self.bind_item(to_class=MyClass),
                            self.bind_item(to_class=MySubClass),
                            self.bind_item(to_instance=my_instance),
                            self.bind_item(to_provider=MyProvider),
                            self.bind_item(to_provider=MyProvider2()),
                        ],
                    ),
                )
                self.bind(MyParentClass)

        injector = Injector([NewModule()])
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent.param, list)
        self.assertEqual(5, len(parent.param))
        self.assertIsInstance(parent.param[0], MyClass)
        self.assertIsInstance(parent.param[1], MySubClass)
        self.assertIs(parent.param[2], my_instance)
        self.assertIs(parent.param[3], my_instance_2)
        self.assertIs(parent.param[4], my_instance_3)

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
        optional_list_param = cast(List[MyClass], parent.optional_list_param)
        self.assertEqual(1, len(optional_list_param))
        self.assertIsInstance(optional_list_param[0], MyClass)
        list_optional_param = cast(List[MyClass], parent.list_optional_param)
        self.assertEqual(1, len(list_optional_param))
        self.assertIsInstance(list_optional_param[0], MyClass)
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

        injector = Injector(
            bindings=[
                SelfBinding(MySubType),
                ClassBinding(MyClass, MySubType),
            ]
        )
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
                self.bind(MyClass, to_class=MyCompositeClass)

        class Module2(Module):
            def configure(self) -> None:
                self.bind(MyOtherClass, to_class=MyCompositeClass)

        injector = Injector(
            [
                Module1(),
                Module2(),
            ]
        )
        instance_1 = injector.inject(MyClass)
        instance_2 = injector.inject(MyOtherClass)
        self.assertIs(instance_1, instance_2)

    def test_generic_type_parameter_injection(self):
        MyTypeVar = TypeVar("MyTypeVar")

        class MyGeneric(Generic[MyTypeVar]):
            pass

        class MyClass1:
            def __init__(self, my_param: MyGeneric):  # type: ignore[type-arg]
                self.my_param = my_param

        class MyClass2:
            def __init__(self, my_param: MyGeneric[str]):
                self.my_param = my_param

        class MyClass3:
            def __init__(self, my_param: MyGeneric[MyTypeVar]):
                self.my_param = my_param

        with self.assertRaises(NonInjectableTypeError):
            Injector(
                bindings=[
                    SelfBinding(MyGeneric),
                    SelfBinding(MyClass2),
                ]
            )

        with self.assertRaises(NonInjectableTypeError):
            Injector(
                bindings=[
                    SelfBinding(MyGeneric),
                    SelfBinding(MyClass3),
                ]
            )

        injector = self.get_injector(MyGeneric, MyClass1)
        my_generic = injector.inject(MyGeneric)
        self.assertIsInstance(my_generic, MyGeneric)
        my_instance_1 = injector.inject(MyClass1)
        self.assertIsInstance(my_instance_1, MyClass1)

    def test_named_arg(self):
        class Class1:
            @named_arg("my_param_1", "new_param_1")
            @named_arg("my_param_2", "new_param_2")
            def __init__(self, my_param_1: str, my_param_2: str, my_param_3: str, my_param_4: str):
                self.my_param_1 = my_param_1
                self.my_param_2 = my_param_2
                self.my_param_3 = my_param_3
                self.my_param_4 = my_param_4

        injector = Injector(
            bindings=[
                InstanceBinding(str, "param_1", named="new_param_1"),
                InstanceBinding(str, "unused_param_1", named="param_1"),
                InstanceBinding(str, "param_2", named="new_param_2"),
                InstanceBinding(str, "param_3", named="my_param_3"),
                InstanceBinding(str, "param_4"),
                SelfBinding(Class1),
            ]
        )
        instance = injector.inject(Class1)
        self.assertIsInstance(instance, Class1)
        self.assertEqual("param_1", instance.my_param_1)
        self.assertEqual("param_2", instance.my_param_2)
        self.assertEqual("param_3", instance.my_param_3)
        self.assertEqual("param_4", instance.my_param_4)

    def test_named_list(self):
        class Class1:
            @named_arg("my_param", "type_1")
            @named_arg("my_other_param", "type_2")
            def __init__(
                self,
                my_param: List[str],
                my_other_param: List[str],
                my_default_param: List[str],
            ):
                self.my_param = my_param
                self.my_other_param = my_other_param
                self.my_default_param = my_default_param

        injector = Injector(
            bindings=[
                SelfBinding(Class1),
                MultiBinding(
                    str,
                    [
                        ItemBinding(bound_instance="my_type_1"),
                    ],
                    named="type_1",
                ),
                MultiBinding(
                    str,
                    [
                        ItemBinding(bound_instance="my_type_2"),
                    ],
                    named="type_2",
                ),
                MultiBinding(
                    str,
                    [
                        ItemBinding(bound_instance="my_default"),
                    ],
                ),
            ]
        )
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

        Injector(
            bindings=[
                SelfBinding(MyOtherClass, scope=ImmediateScope),
            ]
        )

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

        injector = Injector(
            bindings=[
                SelfBinding(MyClass),
                ProviderBinding(MyParent, MyParentProvider),
            ]
        )
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

        injector = Injector(
            bindings=[
                InstanceBinding(MyParentProvider, MyParentProvider(MyClass())),
                ProviderBinding(MyParent, MyParentProvider),
            ]
        )
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

        injector = Injector(
            bindings=[
                ProviderBinding(MyParent, MyParentProvider(MyClass())),
            ]
        )
        my_parent = injector.inject(MyParent)
        self.assertIsInstance(my_parent.my_arg, MyClass)
        self.assertEqual("hello", my_parent.my_str)

    def test_function_provider(self):
        class MyParent:
            def __init__(self, my_arg: MyClass, my_str: str):
                self.my_arg = my_arg
                self.my_str = my_str

        def my_parent_provider(my_arg: MyClass):
            return MyParent(my_arg, "hello")

        injector = Injector(
            bindings=[
                ProviderBinding(MyParent, my_parent_provider),
                SelfBinding(MyClass),
            ]
        )
        my_parent = injector.inject(MyParent)
        self.assertIsInstance(my_parent.my_arg, MyClass)
        self.assertEqual("hello", my_parent.my_str)

    def test_method_provider(self):
        class MyParent:
            def __init__(self, my_arg: MyClass, my_str: str):
                self.my_arg = my_arg
                self.my_str = my_str

        class MyModule(Module):
            def my_parent_provider(self, my_arg: MyClass):
                return MyParent(my_arg, "hello")

            def configure(self) -> None:
                self.bind(MyParent, to_provider=self.my_parent_provider)
                self.bind(MyClass)

        injector = Injector([MyModule])
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

        injector = Injector(
            bindings=[
                SelfBinding(MyClass),
                SelfBinding(MyParentA),
                SelfBinding(MyParentB),
            ]
        )
        my_parent_a = injector.inject(MyParentA)
        my_parent_b = injector.inject(MyParentB)

        self.assertIs(my_parent_a.my_arg, my_parent_b.my_arg)

    def test_named_singleton(self):
        class MyParentA:
            @named_arg("my_arg", "name_1")
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        class MyParentB:
            @named_arg("my_arg", "name_2")
            def __init__(self, my_arg: MyClass):
                self.my_arg = my_arg

        injector = Injector(
            bindings=[
                SelfBinding(MyClass, named="name_1"),
                SelfBinding(MyClass, named="name_2"),
                SelfBinding(MyParentA),
                SelfBinding(MyParentB),
            ]
        )
        my_parent_a = injector.inject(MyParentA)
        my_parent_b = injector.inject(MyParentB)

        self.assertIsNot(my_parent_a.my_arg, my_parent_b.my_arg)

    def test_inject_list_with_singleton_items(self):
        class SubClass1(MyClass):
            pass

        class SubClass2(MyClass):
            pass

        injector = Injector(
            bindings=[MultiBinding(MyClass, [ItemBinding(bound_class=SubClass1), ItemBinding(bound_class=SubClass2)])]
        )
        list_1 = injector.inject(List[MyClass])
        list_2 = injector.inject(List[MyClass])

        self.assertEqual(2, len(list_1))
        self.assertEqual(2, len(list_2))
        self.assertIsInstance(list_1[0], SubClass1)
        self.assertIs(list_1[0], list_2[0])
        self.assertIsInstance(list_1[1], SubClass2)
        self.assertIs(list_1[1], list_2[1])

    def test_list_injection_item_singletons(self):
        injector = Injector(bindings=[MultiBinding(MyClass, [ItemBinding(bound_class=MyClass)])])
        list_instance = injector.inject(List[MyClass])
        tuple_instance = injector.inject(Tuple[MyClass])
        self.assertIs(list_instance[0], tuple_instance[0])

    def test_multi_binding_adding_same_binding(self):
        class Module1(Module):
            def configure(self) -> None:
                self.multi_bind(MyClass, [self.bind_item(to_class=MyClass)])

        class Module2(Module):
            def configure(self) -> None:
                self.multi_bind(MyClass, [self.bind_item(to_class=MyClass)], override_bindings=True)

        injector = Injector(
            [Module1(), Module2()],
        )
        instance = injector.inject(List[MyClass])
        self.assertEqual(1, len(instance))

    def test_private_module_does_not_expose_bindings(self):
        instance_1 = MyClass()

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.bind(MyClass, to_instance=instance_1)

        injector = Injector([MyPrivateModule()])
        with self.assertRaises(NonInjectableTypeError):
            injector.inject(MyClass)

    def test_private_module_does_not_expose_self_bindings(self):
        class MySubClass(MyClass):
            pass

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(self.bind(MyClass, to_class=MySubClass))

        injector = Injector([MyPrivateModule()])
        with self.assertRaises(NonInjectableTypeError):
            injector.inject(MySubClass)

    def test_private_module_uses_exposed_bindings(self):
        instance_1 = MyClass()

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(self.bind(MyClass, to_instance=instance_1))

        injector = Injector([MyPrivateModule()])
        instance = injector.inject(MyClass)
        self.assertIs(instance_1, instance)

    def test_private_module_use_private_binding_through_exposed_binding(self):
        class MyParentClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(self.bind(MyParentClass))
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
                self.expose(self.bind(MyParentClass))

        injector = Injector([MyPrivateModule()], [SelfBinding(MyClass)])
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
        injector = Injector(bindings=[ProviderBinding(MyClass, provider), SelfBinding(MyParentClass)])
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIs(parent.my_param, provider)
        instance = parent.my_param.get()
        self.assertIsInstance(instance, MyClass)

    def test_args_injection(self):
        class MyParentClass:
            def __init__(self, *my_param: MyClass):
                self.my_param = my_param

        parent = self.get_injector(MyClass, MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, tuple)
        self.assertIsInstance(parent.my_param[0], MyClass)

    def test_args_injection_without_binding(self):
        class MyParentClass:
            def __init__(self, *my_param: MyClass):
                self.my_param = my_param

        parent = self.get_injector(MyParentClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertEqual(tuple(), parent.my_param)

    def test_args_injection_with_multi_binding(self):
        class MyParentClass:
            def __init__(self, *my_param: MyClass):
                self.my_param = my_param

        injector = Injector(
            bindings=[
                SelfBinding(MyParentClass),
                MultiBinding(MyClass, [ItemBinding(bound_instance=MyClass())]),
            ]
        )
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, tuple)
        self.assertIsInstance(parent.my_param[0], MyClass)

    def test_injection_with_string_type(self):
        class MyParentClass:
            def __init__(self, my_param: "MyClass"):
                self.my_param = my_param

        parent = self.get_injector(MyParentClass, MyClass).inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, MyClass)

    def test_injection_with_string_type_cache(self):
        class MyParentClass:
            def __init__(self, my_param: "MyClass"):
                self.my_param = my_param

        class MyOtherParentClass:
            def __init__(self, my_param: MyClass):
                self.my_param = my_param

        injector = self.get_injector(MyParentClass, MyOtherParentClass, MyClass)
        parent = injector.inject(MyParentClass)
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.my_param, MyClass)
        other_parent = injector.inject(MyOtherParentClass)
        self.assertIsInstance(other_parent, MyOtherParentClass)
        self.assertIsInstance(other_parent.my_param, MyClass)
        self.assertIs(parent.my_param, other_parent.my_param)

    def test_private_module_multi_bind(self):
        class DependencyClass:
            pass

        class MySubClass1(MyClass):
            def __init__(self, arg: DependencyClass):
                MyClass.__init__(self)
                self.arg = arg

        class MySubClass2(MyClass):
            def __init__(self, arg: DependencyClass):
                MyClass.__init__(self)
                self.arg = arg

        class MyModule1(PrivateModule):
            def configure(self) -> None:
                self.expose(self.multi_bind(MyClass, [self.bind_item(to_class=MySubClass1)]))
                self.bind(DependencyClass)

        class MyModule2(PrivateModule):
            def configure(self) -> None:
                self.expose(
                    self.multi_bind(
                        MyClass,
                        [self.bind_item(to_class=MySubClass2)],
                        override_bindings=False,
                    )
                )
                self.bind(DependencyClass)

        injector = Injector([MyModule1(), MyModule2()])
        instances = injector.inject(List[MyClass])
        self.assertEqual(2, len(instances))
        self.assertIsInstance(instances[0], MySubClass1)
        self.assertIsInstance(instances[1], MySubClass2)
        self.assertIsNot(instances[0].arg, instances[1].arg)

    def test_shared_singleton_with_multi_bind(self):
        class MySubClass1(MyClass):
            pass

        class MySubClass2(MyClass):
            pass

        class MyParentClass:
            def __init__(self, arg: MySubClass1):
                self.arg = arg

        class MyLastParentClass:
            def __init__(self, arg: MySubClass2):
                self.arg = arg

        class MyOtherParentClass:
            def __init__(self, arg: List[MyClass]):
                self.arg = arg

        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyParentClass)
                self.bind(MyOtherParentClass)
                self.bind(MyLastParentClass)
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2),
                    ],
                )

        injector = Injector([MyModule()])
        parent = injector.inject(MyParentClass)
        other_parent = injector.inject(MyOtherParentClass)
        last_parent = injector.inject(MyLastParentClass)
        self.assertIsInstance(parent.arg, MySubClass1)
        self.assertIsInstance(last_parent.arg, MySubClass2)
        self.assertEqual(2, len(other_parent.arg))
        self.assertIsInstance(other_parent.arg[0], MySubClass1)
        self.assertIsInstance(other_parent.arg[1], MySubClass2)
        self.assertIs(parent.arg, other_parent.arg[0])
        self.assertIs(last_parent.arg, other_parent.arg[1])

    def test_shared_item_with_multi_binds(self):
        class MySubClass1(MyClass):
            pass

        class MySubClass2(MyClass):
            pass

        class MyModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2, named=None),
                    ],
                    named="name_1",
                )
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2, named=None),
                    ],
                    named="name_2",
                )

        injector = Injector([MyModule()])
        list_1 = injector.inject(List[MyClass], named="name_1")
        list_2 = injector.inject(List[MyClass], named="name_2")
        item_1 = injector.inject(MySubClass1, named="name_1")
        item_2 = injector.inject(MySubClass2)

        self.assertEqual(2, len(list_1))
        self.assertEqual(2, len(list_2))
        self.assertIsInstance(list_1[0], MySubClass1)
        self.assertIsInstance(list_1[1], MySubClass2)
        self.assertIsInstance(list_2[0], MySubClass1)
        self.assertIsInstance(list_2[1], MySubClass2)
        self.assertIsNot(list_1[0], list_2[0])
        self.assertIs(list_1[0], item_1)
        self.assertIs(list_1[1], list_2[1])
        self.assertIs(list_1[1], item_2)

    def test_scoped_item_binding(self):
        class MySubClass1(MyClass):
            pass

        class MySubClass2(MyClass):
            pass

        class MyModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2, scope=SingletonScope),
                    ],
                    scope=PerLookupScope,
                )

        injector = Injector([MyModule()])
        list_1 = injector.inject(List[MyClass])
        list_2 = injector.inject(List[MyClass])

        self.assertEqual(2, len(list_1))
        self.assertEqual(2, len(list_2))
        self.assertIsInstance(list_1[0], MySubClass1)
        self.assertIsInstance(list_1[1], MySubClass2)
        self.assertIsInstance(list_2[0], MySubClass1)
        self.assertIsInstance(list_2[1], MySubClass2)
        self.assertIsNot(list_1[0], list_2[0])
        self.assertIs(list_1[1], list_2[1])

    def test_shared_module_with_multi_bind(self):
        class MySubClass1(MyClass):
            pass

        class MySubClass2(MyClass):
            pass

        class MyModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2),
                    ],
                )

        injector = Injector([MyModule, MyModule])
        subclasses = injector.inject(List[MyClass])
        self.assertEqual(2, len(subclasses))
        self.assertIsInstance(subclasses[0], MySubClass1)
        self.assertIsInstance(subclasses[1], MySubClass2)

    def test_shared_module_with_multi_bind_2(self):
        class MySubClass1(MyClass):
            pass

        class MySubClass2(MyClass):
            pass

        class MyModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=MySubClass1),
                        self.bind_item(to_class=MySubClass2),
                    ],
                    override_bindings=True,
                )

        class Module1(Module):
            def configure(self) -> None:
                self.install(MyModule)

        class Module2(Module):
            def configure(self) -> None:
                self.install(MyModule)

        injector = Injector([Module1, Module2])
        subclasses = injector.inject(List[MyClass])
        self.assertEqual(2, len(subclasses))
        self.assertIsInstance(subclasses[0], MySubClass1)
        self.assertIsInstance(subclasses[1], MySubClass2)

    def test_cyclic_dependencies_raise_exception(self):
        class MyOtherClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyImpl(MyClass):
            def __init__(self, arg: MyOtherClass):
                MyClass.__init__(self)
                self.arg = arg

        with self.assertRaises(CyclicDependencyError):
            Injector(bindings=[ClassBinding(MyClass, MyImpl), SelfBinding(MyOtherClass)])

    def test_cyclic_dependencies_with_private_module_are_handled(self):
        class MyOtherClass:
            def __init__(self, arg: MyClass):
                self.arg = arg

        class MyImpl(MyClass):
            def __init__(self, arg: MyOtherClass):
                MyClass.__init__(self)
                self.arg = arg

        class MyPrivateModule(PrivateModule):
            def configure(self) -> None:
                self.expose(self.bind(MyOtherClass))
                self.bind(MyClass)

        injector = Injector([MyPrivateModule()], [ClassBinding(MyClass, MyImpl)])
        my_impl = injector.inject(MyClass)
        self.assertIsInstance(my_impl, MyImpl)
        self.assertIsInstance(my_impl.arg, MyOtherClass)
        self.assertIsInstance(my_impl.arg.arg, MyClass)

    def test_builtin_parameters_self_binding_is_not_created(self):
        class MyOtherClass:
            def __init__(
                self,
                param_1: Optional[int] = 1,
                param_2: str = "bye",
                param_3: Optional[List] = None,  # type: ignore[type-arg]
            ):
                self.param_1 = param_1
                self.param_2 = param_2
                self.param_3 = param_3

        CustomT = TypeVar("CustomT")

        class MyModule(Module):
            def configure(self) -> None:
                self.bind(Optional[MyClass], to_instance=None)
                self.bind(CustomT, to_instance="hello")
                self.bind(List[int], to_instance=[2])
                self.bind(MyOtherClass)

        injector = Injector([MyModule])
        instance = injector.inject(MyOtherClass)
        self.assertEqual(instance.param_1, 1)
        self.assertEqual(instance.param_2, "bye")
        self.assertIsNone(instance.param_3)

    def test_loading_string_from_env_var(self):
        # pylint: disable=invalid-name
        @attr.s(auto_attribs=True)
        class MyEnvClass:
            my_key: str
            my_key_123: str
            my_key123something: str
            SomeUpperCamel: str
            someCamel: str
            some123Camel: str
            someABCamel: str
            SOME_UPPER_CASE: str
            SOME_UPPER123CASE: str

        os.environ.update(
            {
                "MY_ENV_CLASS_MY_KEY": "my_key_value",
                "MY_ENV_CLASS_MY_KEY_123": "my_key_123_value",
                "MY_ENV_CLASS_MY_KEY_123_SOMETHING": "my_key_123_something_value",
                "MY_ENV_CLASS_SOME_UPPER_CAMEL": "some_upper_camel_value",
                "MY_ENV_CLASS_SOME_CAMEL": "some_camel_value",
                "MY_ENV_CLASS_SOME_123_CAMEL": "some_123_camel_value",
                "MY_ENV_CLASS_SOME_AB_CAMEL": "some_ab_camel_value",
                "MY_ENV_CLASS_SOME_UPPER_CASE": "some_upper_case_value",
                "MY_ENV_CLASS_SOME_UPPER_123_CASE": "some_upper_123_case_value",
            }
        )

        injector = Injector(bindings=[SelfBinding(MyEnvClass)])
        instance = injector.inject(MyEnvClass)
        self.assertEqual(
            MyEnvClass(
                "my_key_value",
                "my_key_123_value",
                "my_key_123_something_value",
                "some_upper_camel_value",
                "some_camel_value",
                "some_123_camel_value",
                "some_ab_camel_value",
                "some_upper_case_value",
                "some_upper_123_case_value",
            ),
            instance,
        )

    def test_loading_from_env_var_overrides_default(self):
        @attr.s(auto_attribs=True)
        class MyEnvClass:
            my_key: str = "default"

        os.environ.update(
            {
                "MY_ENV_CLASS_MY_KEY": "my_key_value",
            }
        )

        injector = Injector(bindings=[SelfBinding(MyEnvClass)])
        instance = injector.inject(MyEnvClass)
        self.assertEqual(
            MyEnvClass(
                "my_key_value",
            ),
            instance,
        )

    def test_loading_from_env_var_overrides_binding(self):
        @attr.s(auto_attribs=True)
        class MyEnvClass:
            my_key: str

        os.environ.update(
            {
                "MY_ENV_CLASS_MY_KEY": "my_key_value",
            }
        )

        injector = Injector(
            bindings=[
                SelfBinding(MyEnvClass),
                InstanceBinding(str, "some_value", named="my_key"),
                InstanceBinding(str, "some_value"),
            ]
        )
        instance = injector.inject(MyEnvClass)
        self.assertEqual(
            MyEnvClass(
                "my_key_value",
            ),
            instance,
        )

    def test_loading_types_from_env_var(self):
        @attr.s(auto_attribs=True)
        class MyEnvClass:
            some_int: int
            some_float: float
            some_bool: bool
            some_bool_2: bool
            some_bool_3: bool
            some_bool_4: bool
            some_bool_5: bool
            some_bool_6: bool
            some_optional: Optional[str]

        os.environ.update(
            {
                "MY_ENV_CLASS_SOME_INT": "42",
                "MY_ENV_CLASS_SOME_FLOAT": "1.345",
                "MY_ENV_CLASS_SOME_BOOL": "true",
                "MY_ENV_CLASS_SOME_BOOL_2": "false",
                "MY_ENV_CLASS_SOME_BOOL_3": "True",
                "MY_ENV_CLASS_SOME_BOOL_4": "False",
                "MY_ENV_CLASS_SOME_BOOL_5": "0",
                "MY_ENV_CLASS_SOME_BOOL_6": "1",
                "MY_ENV_CLASS_SOME_OPTIONAL": "test_value",
            }
        )

        injector = Injector(bindings=[SelfBinding(MyEnvClass)])
        instance = injector.inject(MyEnvClass)
        self.assertEqual(
            MyEnvClass(
                42,
                1.345,
                True,
                False,
                True,
                False,
                False,
                True,
                "test_value",
            ),
            instance,
        )

    def test_loading_named_parameters_from_env_var(self):
        class MyEnvClass:
            @named_arg("some_key", "renamed_key")
            def __init__(self, some_key: str):
                self.key = some_key

        os.environ.update(
            {
                "MY_ENV_CLASS_RENAMED_KEY": "renamed_value",
            }
        )

        injector = Injector(bindings=[SelfBinding(MyEnvClass)])
        instance = injector.inject(MyEnvClass)
        self.assertEqual("renamed_value", instance.key)

    def test_context_scope(self):
        class MyOtherClass:
            pass

        injector = Injector(
            bindings=[
                SelfBinding(MyClass),
                SelfBinding(MyOtherClass, scope=ContextScope),
            ]
        )
        scope = injector.inject(ContextScope)

        instance_1 = injector.inject(MyClass)
        other_instance_1 = injector.inject(MyOtherClass)

        with scope:
            instance_2 = injector.inject(MyClass)
            other_instance_2 = injector.inject(MyOtherClass)

            instance_3 = injector.inject(MyClass)
            other_instance_3 = injector.inject(MyOtherClass)

        instance_4 = injector.inject(MyClass)
        other_instance_4 = injector.inject(MyOtherClass)
        self.assertIs(instance_1, instance_2)
        self.assertIs(instance_1, instance_3)
        self.assertIs(instance_1, instance_4)
        self.assertIsNot(other_instance_1, other_instance_2)
        self.assertIs(other_instance_2, other_instance_3)
        self.assertIsNot(other_instance_1, other_instance_4)
        self.assertIsNot(other_instance_2, other_instance_4)

    def test_multi_provider_injection(self):
        class MultiModule(Module):
            def configure(self) -> None:
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_provider=self.provider_1),
                        self.bind_item(to_provider=self.provider_2),
                        self.bind_item(to_provider=self.provider_1),
                    ],
                )

            def provider_1(self):
                return MyClass()

            def provider_2(self):
                return MyClass()

        injector = Injector([MultiModule()])
        result = injector.inject(List[MyClass])
        self.assertEqual(3, len(result))
        self.assertIsNot(result[0], result[1])
        self.assertIs(result[0], result[2])

    def test_multi_provider_shared_injection(self):
        class MultiModule(Module):
            def configure(self) -> None:
                self.bind(MyClass, to_provider=self.provider_1)
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_provider=self.provider_1),
                    ],
                )

            def provider_1(self):
                return MyClass()

        injector = Injector([MultiModule()])
        list_result = injector.inject(List[MyClass])
        instance = injector.inject(MyClass)
        self.assertIs(list_result[0], instance)

    def test_multi_class_injection(self):
        class SubClass1(MyClass):
            pass

        class SubClass2(MyClass):
            pass

        class MultiModule(Module):
            def configure(self) -> None:
                self.bind(MyClass, to_class=SubClass1)
                self.multi_bind(
                    MyClass,
                    [
                        self.bind_item(to_class=SubClass1),
                        self.bind_item(to_class=SubClass2),
                        self.bind_item(to_class=SubClass1),
                    ],
                )

        injector = Injector([MultiModule()])
        result = injector.inject(List[MyClass])
        instance = injector.inject(MyClass)
        self.assertEqual(3, len(result))
        self.assertIsNot(result[0], result[1])
        self.assertIs(result[0], result[2])
        self.assertIs(result[2], instance)
