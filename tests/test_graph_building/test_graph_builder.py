import unittest
from typing import List, Optional, Set, Tuple, Type, cast
from unittest.mock import ANY

from illuin_inject import SingletonScope, ThreadScope, annotated_arg
from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import ClassBinding, FactoryBinding, InstanceBinding
from illuin_inject.dependency_graph import ClassBindingNode, CollectionBindingNode, DependencyGraph, \
    FactoryBindingNode, InstanceBindingNode, ParameterNode
from illuin_inject.exceptions import BindingError, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.graph_building.graph_builder import GraphBuilder
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
                Target(MyType): [InstanceBindingNode(self.my_instance_binding)],
                Target(MyOtherType): [InstanceBindingNode(self.my_other_instance_binding)]
            }), graph,
        )

    def test_get_graph_with_annotated_bindings(self):
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(self.my_annotated_instance_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [InstanceBindingNode(self.my_instance_binding)],
                Target(MyType, "my_annotation"): [InstanceBindingNode(self.my_annotated_instance_binding)]
            }), graph,
        )

    def test_get_multiple_bindings_for_type_keeps_order(self):
        my_class_binding = ClassBinding(MyType)
        self.binding_registry.register(my_class_binding)
        self.binding_registry.register(self.my_instance_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [ClassBindingNode(my_class_binding), InstanceBindingNode(self.my_instance_binding)],
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
                    ClassBindingNode(my_type_binding)
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
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
                    ClassBindingNode(my_type_binding)
                ],
                Target(MyType, "my_annotation"): [
                    ClassBindingNode(my_type_annotated_binding)
                ],
                Target(MyParentClass, "my_annotation"): [
                    ClassBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass, "my_annotation")][0]) \
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
                    ClassBindingNode(my_type_binding)
                ],
                Target(MyType, "my_annotation"): [
                    ClassBindingNode(my_type_annotated_binding)
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_type_annotated_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
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
                    ClassBindingNode(my_type_binding)
                ],
                Target(MyOtherType): [
                    ClassBindingNode(my_other_type_binding),
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        my_parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_type_binding),
                            )
                        ],
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_other_type_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter_arg = cast(ClassBindingNode,
                             graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter_arg.name)
        parameter_kwarg = cast(ClassBindingNode,
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
                    ClassBindingNode(my_type_binding),
                ],
                Target(MyOtherType): [
                    ClassBindingNode(my_other_type_binding)
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_type_binding),
                            ),
                            ParameterNode(
                                ANY,
                                ClassBindingNode(my_other_type_binding),
                            ),
                        ])
                ],
            }), graph,
        )
        parameter_1 = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
        self.assertEqual("my_param", parameter_1.name)
        parameter_2 = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[1].parameter
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
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                InstanceBindingNode(InstanceBinding(int, 1)),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
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
                    InstanceBindingNode(self.my_instance_binding),
                    ClassBindingNode(ClassBinding(MyType)),
                ],
                Target(List[MyType]): [
                    InstanceBindingNode(list_instance_binding),
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                InstanceBindingNode(list_instance_binding),
                            )
                        ])
                ],
            }), graph,
        )
        parameter = cast(ClassBindingNode, graph.binding_nodes_by_target[Target(MyParentClass)][0]).args[0].parameter
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
                    InstanceBindingNode(self.my_instance_binding),
                    ClassBindingNode(ClassBinding(MyType)),
                ],
                Target(List[MyType]): [
                    CollectionBindingNode(
                        [
                            InstanceBindingNode(self.my_instance_binding),
                            ClassBindingNode(ClassBinding(MyType)),
                        ],
                        list,
                    )
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                CollectionBindingNode(
                                    [
                                        InstanceBindingNode(self.my_instance_binding),
                                        ClassBindingNode(ClassBinding(MyType)),
                                    ],
                                    list,
                                )
                            )
                        ])
                ],
            }), graph,
        )

    def test_set_binding_without_explicit_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Set[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    InstanceBindingNode(self.my_instance_binding),
                    ClassBindingNode(ClassBinding(MyType)),
                ],
                Target(Set[MyType]): [
                    CollectionBindingNode(
                        [
                            InstanceBindingNode(self.my_instance_binding),
                            ClassBindingNode(ClassBinding(MyType)),
                        ],
                        set,
                    )
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                CollectionBindingNode(
                                    [
                                        InstanceBindingNode(self.my_instance_binding),
                                        ClassBindingNode(ClassBinding(MyType)),
                                    ],
                                    set,
                                )
                            )
                        ])
                ],
            }),
            graph,
        )

    def test_tuple_binding_without_explicit_binding(self):
        class MyParentClass:
            def __init__(self, my_param: Tuple[MyType]):
                self.my_param = my_param

        parent_class_binding = ClassBinding(MyParentClass)
        self.binding_registry.register(self.my_instance_binding)
        self.binding_registry.register(ClassBinding(MyType))
        self.binding_registry.register(parent_class_binding)

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    InstanceBindingNode(self.my_instance_binding),
                    ClassBindingNode(ClassBinding(MyType)),
                ],
                Target(Tuple[MyType]): [
                    CollectionBindingNode(
                        [
                            InstanceBindingNode(self.my_instance_binding),
                            ClassBindingNode(ClassBinding(MyType)),
                        ],
                        tuple,
                    )
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                CollectionBindingNode(
                                    [
                                        InstanceBindingNode(self.my_instance_binding),
                                        ClassBindingNode(ClassBinding(MyType)),
                                    ],
                                    tuple,
                                )
                            )
                        ])
                ],
            }),
            graph,
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
                    InstanceBindingNode(self.my_instance_binding),
                ],
                Target(Optional[MyType]): [
                    InstanceBindingNode(self.my_instance_binding)
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                InstanceBindingNode(self.my_instance_binding)
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
                    InstanceBindingNode(self.my_instance_binding),
                    ClassBindingNode(ClassBinding(MyType, SubType))
                ],
                Target(Type[MyType]): [
                    InstanceBindingNode(InstanceBinding(Type[MyType], SubType))
                ],
                Target(MyParentClass): [
                    ClassBindingNode(
                        parent_class_binding,
                        [
                            ParameterNode(
                                ANY,
                                InstanceBindingNode(InstanceBinding(Type[MyType], SubType))
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

        graph = self.graph_builder.get_dependency_graph()
        self.assertEqual(
            DependencyGraph({
                Target(MyType): [
                    InstanceBindingNode(self.my_instance_binding),
                ],
                Target(MyFactory): [
                    ClassBindingNode(
                        ClassBinding(MyFactory),
                        [
                            ParameterNode(
                                ANY,
                                InstanceBindingNode(self.my_instance_binding)
                            )
                        ]
                    ),
                ],
                Target(MyInjectee): [
                    FactoryBindingNode(
                        factory_binding,
                        ClassBindingNode(
                            ClassBinding(MyFactory),
                            [
                                ParameterNode(
                                    ANY,
                                    InstanceBindingNode(self.my_instance_binding)
                                )
                            ]
                        ),
                    )
                ],
            }), graph,
        )
