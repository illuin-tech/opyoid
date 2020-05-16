import unittest
from inspect import Parameter
from typing import Any, List, Set, Tuple, Type

from illuin_inject import PerLookupScope, SingletonScope
from illuin_inject.bindings import ClassBinding, FactoryBinding, InstanceBinding
from illuin_inject.dependency_graph import BindingNode, ClassBindingNode, CollectionBindingNode, DependencyGraph, \
    FactoryBindingNode, InstanceBindingNode, ParameterNode
from illuin_inject.exceptions import NoBindingFound, UnexpectedBindingTypeError
from illuin_inject.factory import Factory
from illuin_inject.object_provider import ObjectProvider
from illuin_inject.target import Target


class MyType:
    pass


# pylint: disable=unsupported-assignment-operation
class TestObjectProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.dependency_graph = DependencyGraph()
        self.object_provider = ObjectProvider(self.dependency_graph, {
            SingletonScope: SingletonScope(),
            PerLookupScope: PerLookupScope(),
        })

    def test_provide_from_simple_binding_node(self):
        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            InstanceBindingNode(InstanceBinding(MyType, instance))
        ]
        self.assertIs(instance, self.object_provider.provide(Target(MyType)))

    def test_provide_missing_binding_raises_exception(self):
        with self.assertRaises(NoBindingFound):
            self.object_provider.provide(Target(MyType))

    def test_provide_multiple_bindings(self):
        instance_1 = MyType()
        instance_2 = MyType()

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            InstanceBindingNode(InstanceBinding(MyType, instance_1)),
            InstanceBindingNode(InstanceBinding(MyType, instance_2)),
        ]

        self.assertIs(instance_2, self.object_provider.provide(Target(MyType)))

    def test_provide_from_class_binding(self):
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
        ]

        self.assertIsInstance(self.object_provider.provide(Target(MyType)), MyType)

    def test_provide_from_parameter_node(self):
        class MyOtherType:
            pass

        class MyParentClass:
            def __init__(self, param: MyType, *_args, other_param: MyOtherType):
                self.param = param
                self.other_param = other_param

        self.dependency_graph.binding_nodes_by_target[Target(MyParentClass)] = [
            ClassBindingNode(
                ClassBinding(MyParentClass),
                [
                    ParameterNode(
                        Parameter("param", Parameter.POSITIONAL_OR_KEYWORD),
                        ClassBindingNode(ClassBinding(MyType))
                    )
                ],
                [
                    ParameterNode(
                        Parameter("other_param", Parameter.VAR_KEYWORD),
                        ClassBindingNode(ClassBinding(MyOtherType)),
                    )
                ]
            ),
        ]
        parent = self.object_provider.provide(Target(MyParentClass))
        self.assertIsInstance(parent, MyParentClass)
        self.assertIsInstance(parent.param, MyType)
        self.assertIsInstance(parent.other_param, MyOtherType)

    def test_provide_list_from_type(self):
        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]
        my_list = self.object_provider.provide(Target(List[MyType]))
        self.assertIsInstance(my_list, list)
        self.assertEqual(2, len(my_list))
        self.assertIsNot(instance, my_list[0])
        self.assertIsInstance(my_list[0], MyType)
        self.assertIs(instance, my_list[1])

    def test_provide_set_from_type(self):
        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]
        my_set = self.object_provider.provide(Target(Set[MyType]))
        self.assertIsInstance(my_set, set)
        self.assertEqual(2, len(list(my_set)))
        self.assertIn(instance, my_set)

    def test_provide_tuple_from_type(self):
        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]
        my_tuple = self.object_provider.provide(Target(Tuple[MyType]))
        self.assertIsInstance(my_tuple, tuple)
        self.assertEqual(2, len(my_tuple))
        self.assertIsNot(instance, my_tuple[0])
        self.assertIsInstance(my_tuple[0], MyType)
        self.assertIs(instance, my_tuple[1])

    def test_provide_list_from_list(self):
        instance = MyType()
        instance_2 = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]
        self.dependency_graph.binding_nodes_by_target[Target(List[MyType])] = [
            InstanceBindingNode(InstanceBinding(List[MyType], [instance_2])),
        ]
        my_list = self.object_provider.provide(Target(List[MyType]))
        self.assertEqual(1, len(my_list))
        self.assertIs(instance_2, my_list[0])

    def test_provide_type_from_class(self):
        instance = MyType()

        class SubType(MyType):
            pass

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType, SubType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]

        my_type = self.object_provider.provide(Target(Type[MyType]))
        self.assertEqual(SubType, my_type)

    def test_provide_type_from_type(self):
        instance = MyType()

        class SubType(MyType):
            pass

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType, SubType)),
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]
        self.dependency_graph.binding_nodes_by_target[Target(Type[MyType])] = [
            InstanceBindingNode(InstanceBinding(Type[MyType], MyType)),
        ]

        my_type = self.object_provider.provide(Target(Type[MyType]))
        self.assertIs(MyType, my_type)

    def test_provide_type_from_class_without_class_bindings_raises_exception(self):
        instance = MyType()

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            InstanceBindingNode(InstanceBinding(MyType, instance)),
        ]

        with self.assertRaises(NoBindingFound):
            self.object_provider.provide(Target(Type[MyType]))

    def test_provide_type_list(self):
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            ClassBindingNode(ClassBinding(MyType)),
        ]

        type_list = self.object_provider.provide(Target(List[Type[MyType]]))
        self.assertEqual([MyType], type_list)

    def test_provide_from_collection_binding_node(self):
        class MyParentClass:
            def __init__(self, param: List[MyType]):
                self.param = param

        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyParentClass)] = [
            ClassBindingNode(
                ClassBinding(MyParentClass),
                [
                    ParameterNode(
                        Parameter("param", Parameter.VAR_POSITIONAL),
                        CollectionBindingNode(
                            [
                                ClassBindingNode(ClassBinding(MyType)),
                                InstanceBindingNode(InstanceBinding(MyType, instance)),
                            ],
                            list,
                        )
                    )
                ]
            ),
        ]

        parent = self.object_provider.provide(Target(MyParentClass))
        self.assertEqual(2, len(parent.param))
        self.assertIsInstance(parent.param[0], MyType)
        self.assertIs(instance, parent.param[1])

    def test_provide_factory__with_instance_binding(self):
        class MyClass:
            def __init__(self, my_param: str):
                self.my_param = my_param

        class MyFactory(Factory[MyClass]):
            def create(self) -> MyClass:
                return MyClass("coucou")

        my_factory = MyFactory()
        self.dependency_graph.binding_nodes_by_target[Target(MyClass)] = [
            FactoryBindingNode(
                FactoryBinding(MyClass, my_factory),
                InstanceBindingNode(InstanceBinding(MyFactory, my_factory))
            )
        ]
        my_instance = self.object_provider.provide(Target(MyClass))
        self.assertIsInstance(my_instance, MyClass)
        self.assertEqual("coucou", my_instance.my_param)

    def test_provide_factory_with_class_binding(self):
        class MyClass:
            def __init__(self, my_param: Any):
                self.my_param = my_param

        class MyFactory(Factory[MyClass]):
            def __init__(self, my_type: MyType):
                self.my_type = my_type

            def create(self) -> MyClass:
                return MyClass(self.my_type)

        self.dependency_graph.binding_nodes_by_target[Target(MyClass)] = [
            FactoryBindingNode(
                FactoryBinding(MyClass, MyFactory),
                ClassBindingNode(
                    ClassBinding(MyFactory),
                    [
                        ParameterNode(
                            Parameter("my_type", Parameter.POSITIONAL_OR_KEYWORD),
                            ClassBindingNode(
                                ClassBinding(MyType),
                            ),
                        ),
                    ],
                ),
            ),
        ]
        my_instance = self.object_provider.provide(Target(MyClass))
        self.assertIsInstance(my_instance, MyClass)
        self.assertIsInstance(my_instance.my_param, MyType)

    def test_provide_scoped_factory_binding(self):
        class MyClass:
            def __init__(self, my_param: Any):
                self.my_param = my_param

        class MyFactory(Factory[MyClass]):
            def __init__(self, my_type: MyType):
                self.my_type = my_type

            def create(self) -> MyClass:
                return MyClass(self.my_type)

        self.dependency_graph.binding_nodes_by_target[Target(MyClass)] = [
            FactoryBindingNode(
                FactoryBinding(MyClass, MyFactory, PerLookupScope),
                ClassBindingNode(
                    ClassBinding(MyFactory, scope=PerLookupScope),
                    [
                        ParameterNode(
                            Parameter("my_type", Parameter.POSITIONAL_OR_KEYWORD),
                            ClassBindingNode(
                                ClassBinding(MyType),
                            ),
                        ),
                    ],
                ),
            ),
        ]
        instance_1 = self.object_provider.provide(Target(MyClass))
        self.assertIsInstance(instance_1, MyClass)
        self.assertIsInstance(instance_1.my_param, MyType)
        instance_2 = self.object_provider.provide(Target(MyClass))
        self.assertIsInstance(instance_2, MyClass)
        self.assertIsInstance(instance_2.my_param, MyType)
        self.assertIs(instance_1.my_param, instance_2.my_param)
        self.assertIsNot(instance_1, instance_2)

    def test_provide_from_unknown_binding_node_raises_exception(self):
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            BindingNode(),
        ]
        with self.assertRaises(UnexpectedBindingTypeError):
            self.object_provider.provide(Target(MyType))
