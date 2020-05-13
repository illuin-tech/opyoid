import unittest
from unittest.mock import create_autospec

from illuin_inject.binding_registry import BindingRegistry
from illuin_inject.bindings import Binding
from illuin_inject.exceptions import BindingError
from illuin_inject.graph_building import GraphBuilder
from illuin_inject.graph_building.binding_nodes_factory import FromBindingsBindingNodesFactory
from illuin_inject.target import Target


class TestFromBindingsBindingNodesFactory(unittest.TestCase):
    def setUp(self):
        self.binding_registry = create_autospec(BindingRegistry, spec_set=True)
        self.binding_nodes_factory = FromBindingsBindingNodesFactory(
            self.binding_registry,
            [],
        )
        self.graph_builder = create_autospec(GraphBuilder, spec_set=True)

    def test_unknown_binding_type_raises_binding_error(self):
        self.binding_registry.get_bindings.return_value = [
            Binding(str)
        ]
        with self.assertRaises(BindingError):
            self.binding_nodes_factory.create(Target(str), self.graph_builder)
