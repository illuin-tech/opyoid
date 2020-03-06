import unittest
from inspect import Parameter
from typing import List, Type

from illuin_inject import SingletonScope
from illuin_inject.bindings import ClassBinding, InstanceBinding
from illuin_inject.dependency_graph import CollectionBindingNode, DependencyGraph, ParameterNode, SimpleBindingNode
from illuin_inject.exceptions import NoBindingFound
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
        })

    def test_provide_from_simple_binding_node(self):
        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(InstanceBinding(MyType, instance))
        ]
        self.assertIs(instance, self.object_provider.provide(Target(MyType)))

    def test_provide_missing_binding_raises_exception(self):
        with self.assertRaises(NoBindingFound):
            self.object_provider.provide(Target(MyType))

    def test_provide_multiple_bindings(self):
        instance_1 = MyType()
        instance_2 = MyType()

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(InstanceBinding(MyType, instance_1)),
            SimpleBindingNode(InstanceBinding(MyType, instance_2)),
        ]

        self.assertIs(instance_2, self.object_provider.provide(Target(MyType)))

    def test_provide_from_class_binding(self):
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(ClassBinding(MyType)),
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
            SimpleBindingNode(
                ClassBinding(MyParentClass),
                [
                    ParameterNode(
                        Parameter("param", Parameter.POSITIONAL_OR_KEYWORD),
                        SimpleBindingNode(ClassBinding(MyType))
                    )
                ],
                [
                    ParameterNode(
                        Parameter("other_param", Parameter.VAR_KEYWORD),
                        SimpleBindingNode(ClassBinding(MyOtherType)),
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
            SimpleBindingNode(ClassBinding(MyType)),
            SimpleBindingNode(InstanceBinding(MyType, instance)),
        ]
        my_list = self.object_provider.provide(Target(List[MyType]))
        self.assertEqual(2, len(my_list))
        self.assertIsNot(instance, my_list[0])
        self.assertIsInstance(my_list[0], MyType)
        self.assertIs(instance, my_list[1])

    def test_provide_list_from_list(self):
        instance = MyType()
        instance_2 = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(ClassBinding(MyType)),
            SimpleBindingNode(InstanceBinding(MyType, instance)),
        ]
        self.dependency_graph.binding_nodes_by_target[Target(List[MyType])] = [
            SimpleBindingNode(InstanceBinding(List[MyType], [instance_2])),
        ]
        my_list = self.object_provider.provide(Target(List[MyType]))
        self.assertEqual(1, len(my_list))
        self.assertIs(instance_2, my_list[0])

    def test_provide_type_from_class(self):
        instance = MyType()

        class SubType(MyType):
            pass

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(ClassBinding(MyType, SubType)),
            SimpleBindingNode(InstanceBinding(MyType, instance)),
        ]

        my_type = self.object_provider.provide(Target(Type[MyType]))
        self.assertEqual(SubType, my_type)

    def test_provide_type_from_type(self):
        instance = MyType()

        class SubType(MyType):
            pass

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(ClassBinding(MyType, SubType)),
            SimpleBindingNode(InstanceBinding(MyType, instance)),
        ]
        self.dependency_graph.binding_nodes_by_target[Target(Type[MyType])] = [
            SimpleBindingNode(InstanceBinding(Type[MyType], MyType)),
        ]

        my_type = self.object_provider.provide(Target(Type[MyType]))
        self.assertIs(MyType, my_type)

    def test_provide_type_from_class_without_class_bindings_raises_exception(self):
        instance = MyType()

        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(InstanceBinding(MyType, instance)),
        ]

        with self.assertRaises(NoBindingFound):
            self.object_provider.provide(Target(Type[MyType]))

    def test_provide_type_list(self):
        self.dependency_graph.binding_nodes_by_target[Target(MyType)] = [
            SimpleBindingNode(ClassBinding(MyType)),
        ]

        type_list = self.object_provider.provide(Target(List[Type[MyType]]))
        self.assertEqual([MyType], type_list)

    def test_provide_from_collection_binding_node(self):
        class MyParentClass:
            def __init__(self, param: List[MyType]):
                self.param = param

        instance = MyType()
        self.dependency_graph.binding_nodes_by_target[Target(MyParentClass)] = [
            SimpleBindingNode(
                ClassBinding(MyParentClass),
                [
                    ParameterNode(
                        Parameter("param", Parameter.VAR_POSITIONAL),
                        CollectionBindingNode([
                            SimpleBindingNode(ClassBinding(MyType)),
                            SimpleBindingNode(InstanceBinding(MyType, instance)),
                        ])
                    )
                ]
            ),
        ]

        parent = self.object_provider.provide(Target(MyParentClass))
        self.assertEqual(2, len(parent.param))
        self.assertIsInstance(parent.param[0], MyType)
        self.assertIs(instance, parent.param[1])
