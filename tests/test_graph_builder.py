import unittest
from typing import List, Optional, Type, cast
from unittest.mock import ANY

from illuin_inject import SingletonScope, ThreadScope, annotated_arg
from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import ClassBinding, InstanceBinding
from illuin_inject.dependency_graph import CollectionBindingNode, DependencyGraph, ParameterNode, SimpleBindingNode
from illuin_inject.exceptions import BindingError, NonInjectableTypeError
from illuin_inject.graph_builder import GraphBuilder
from illuin_inject.target import Target


class MyType:
    pass


class MyOtherType:
    pass


# pylint: disable=unsubscriptable-object
class TestGraphBuilder(unittest.TestCase):
    def setUp(self) -> None:
        self.binding_registry = BindingRegistry()
        self.graph_builder = GraphBuilder(self.binding_registry, {SingletonScope: SingletonScope()})
        self.my_instance = MyType()
        self.my_instance_binding = InstanceBinding(MyType, self.my_instance)
        self.my_annotated_instance_binding = InstanceBinding(MyType, self.my_instance, "my_annotation")
        self.my_other_instance = MyOtherType()
        self.my_other_instance_binding = InstanceBinding(MyOtherType, self.my_other_instance)

    def test_get_graph_with_instance_bindings(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(self.my_other_instance_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [SimpleBindingNode(self.my_instance_binding)],
                Target(MyOtherType): [SimpleBindingNode(self.my_other_instance_binding)]
            }), graph,
        )

    def test_get_graph_with_annotated_bindings(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(self.my_annotated_instance_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [SimpleBindingNode(self.my_instance_binding)],
                Target(MyType, "my_annotation"): [SimpleBindingNode(self.my_annotated_instance_binding)]
            }), graph,
        )

    def test_get_multiple_bindings_for_type_keeps_order(self):
        my_class_binding = ClassBinding(MyType)
        self.binding_registry.register(my_class_binding)
        self.binding_registry.register(self.my_instance_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [SimpleBindingNode(my_class_binding), SimpleBindingNode(self.my_instance_binding)],
            }), graph,
        )

    def test_parameter_node(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        my_type_binding = ClassBinding(MyType)
        self.binding_registry.register(my_type_binding)
        self.binding_registry.register(my_parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(my_type_binding)
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter.name)

    def test_parameter_node_with_annotated_parent(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass, annotation="my_annotation")
        my_type_binding = ClassBinding(MyType)
        my_type_annotated_binding = ClassBinding(MyType, annotation="my_annotation")
        self.binding_registry.register(my_parent_class_binding)
        self.binding_registry.register(my_type_binding)
        self.binding_registry.register(my_type_annotated_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(my_type_binding)
                ],
                Target(MyType, "my_annotation"): [
                    SimpleBindingNode(my_type_annotated_binding)
                ],
                Target(MyParentClass, "my_annotation"): [
                    SimpleBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass, "my_annotation")][0]) \
            .args[0].parameter
        self.assertEqual("my_param", parameter.name)

    def test_parameter_node_with_annotated_parameter(self):
        class MyParentClass:
            @annotated_arg("my_param", "my_annotation")
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        my_type_binding = ClassBinding(MyType)
        my_type_annotated_binding = ClassBinding(MyType, annotation="my_annotation")
        self.binding_registry.register(my_parent_class_binding)
        self.binding_registry.register(my_type_binding)
        self.binding_registry.register(my_type_annotated_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(my_type_binding)
                ],
                Target(MyType, "my_annotation"): [
                    SimpleBindingNode(my_type_annotated_binding)
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_type_annotated_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter.name)

    def test_parameter_node_with_keyword_arguments(self):
        class MyParentClass:
            def __init__(self, my_param: MyType, *_args, my_other_param: MyOtherType, **_kwargs):
                self.my_param = my_param
                self.my_other_param = my_other_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        my_type_binding = ClassBinding(MyType)
        my_other_type_binding = ClassBinding(MyOtherType)
        self.binding_registry.register(my_type_binding)
        self.binding_registry.register(my_other_type_binding)
        self.binding_registry.register(my_parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(my_type_binding)
                ],
                Target(MyOtherType): [
                    SimpleBindingNode(my_other_type_binding),
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_type_binding),
                            )
                        ],
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_other_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter_arg = cast(SimpleBindingNode,
                             graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter_arg.name)
        parameter_kwarg = cast(SimpleBindingNode,
                               graph.binding_nodes_by_target[Target(MyParentClass)][0]).kwargs[0].parameter
        self.assertEqual("my_other_param", parameter_kwarg.name)

    def test_parameter_nodes_keep_order(self):
        class MyParentClass:
            def __init__(self, my_param: MyType, my_other_param: MyOtherType):
                self.my_param = my_param
                self.my_other_param = my_other_param

        parent_class_binding = ClassBinding(MyParentClass)
        my_type_binding = ClassBinding(MyType)
        my_other_type_binding = ClassBinding(MyOtherType)
        self.binding_registry.register(my_type_binding)
        self.binding_registry.register(parent_class_binding)
        self.binding_registry.register(my_other_type_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(my_type_binding),
                ],
                Target(MyOtherType): [
                    SimpleBindingNode(my_other_type_binding)
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_type_binding),
                            ),
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(my_other_type_binding),
                            ),
                        ])
                ],
            }), graph,
        )
        parameter_1 = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter_1.name)
        parameter_2 = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[1].parameter
        self.assertEqual("my_other_param", parameter_2.name)

    def test_get_bindings_from_default(self):
        class MyParentClass:
            def __init__(self, my_param: int = 1):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(InstanceBinding(int, 1)),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter.name)

    def test_missing_binding_raises_exception(self):
        class MyParentClass:
            def __init__(self, my_param: MyType):
                self.my_param = my_param

        my_parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(my_parent_class_binding)

        with self.assertRaises(NonInjectableTypeError):
            self.graph_builder.get_dependency_graph()

    def test_list_binding_uses_list_over_item_binding(self):
        class MyParentClass:
            def __init__(self, my_param: List[MyType]):
                self.my_param = my_param

        list_instance_binding = InstanceBinding(List[MyType], [self.my_instance])
        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(list_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(self.my_instance_binding),
                    SimpleBindingNode(ClassBinding(MyType)),
                ],
                Target(List[MyType]): [
                    SimpleBindingNode(list_instance_binding),
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(list_instance_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(SimpleBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter.name)

    def test_list_binding_without_explicit_binding(self):
        class MyParentClass:
            def __init__(self, my_param: List[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(self.my_instance_binding),
                    SimpleBindingNode(ClassBinding(MyType)),
                ],
                Target(List[MyType]): [
                    CollectionBindingNode(
                        [
                            SimpleBindingNode(self.my_instance_binding),
                            SimpleBindingNode(ClassBinding(MyType)),
                        ]
                    )
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                CollectionBindingNode(
                                    [
                                        SimpleBindingNode(self.my_instance_binding),
                                        SimpleBindingNode(ClassBinding(MyType)),
                                    ]
                                )
                            )
                        ])
                ],
            }), graph,
        )

    def test_optional_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Optional[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(self.my_instance_binding),
                ],
                Target(Optional[MyType]): [
                    SimpleBindingNode(self.my_instance_binding)
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(self.my_instance_binding)
                            )
                        ])
                ],
            }), graph,
        )

    def test_type_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Type[MyType]):
                self.my_param = my_param

        class SubType(MyType):
            pass

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType, SubType))
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    SimpleBindingNode(self.my_instance_binding),
                    SimpleBindingNode(ClassBinding(MyType, SubType))
                ],
                Target(Type[MyType]): [
                    SimpleBindingNode(InstanceBinding(Type[MyType], SubType))
                ],
                Target(MyParentClass): [
                    SimpleBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                SimpleBindingNode(InstanceBinding(Type[MyType], SubType))
                            )
                        ])
                ],
            }), graph,
        )

    def test_type_binding_without_class_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Type[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(parent_class_binding)

        with self.assertRaises(NonInjectableTypeError):
            self.graph_builder.get_dependency_graph()

    def test_binding_parameter_without_type(self):
        class MyParentClass:
            def __init__(self, my_param):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(parent_class_binding)

        with self.assertRaises(NonInjectableTypeError):
            self.graph_builder.get_dependency_graph()

    def test_unknown_scope_binding(self):
        self.binding_registry.register(ClassBinding(MyType, scope=ThreadScope))
        with self.assertRaises(BindingError):
            self.graph_builder.get_dependency_graph()
