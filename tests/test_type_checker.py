import unittest
from typing import List, Optional, Set, Tuple, Type, Union

from opyoid import Provider
from opyoid.named import Named
from opyoid.type_checker import PEP_585, TypeChecker


class TestClass:
    pass


class TestTypeChecker(unittest.TestCase):
    def setUp(self) -> None:
        self.type_checker = TypeChecker()

    def test_is_list(self):
        self.assertFalse(self.type_checker.is_list(str))
        self.assertFalse(self.type_checker.is_list(TestClass))
        self.assertTrue(self.type_checker.is_list(List[str]))
        self.assertTrue(self.type_checker.is_list(List[TestClass]))
        self.assertFalse(self.type_checker.is_list(Optional[str]))
        self.assertFalse(self.type_checker.is_list(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_list(Type[str]))
        self.assertFalse(self.type_checker.is_list(Type[TestClass]))
        self.assertFalse(self.type_checker.is_list(Optional[List[Type[TestClass]]]))
        self.assertTrue(self.type_checker.is_list(List[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_list(Set[TestClass]))
        self.assertFalse(self.type_checker.is_list(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_list(Named[TestClass]))

    def test_is_optional(self):
        self.assertFalse(self.type_checker.is_optional(str))
        self.assertFalse(self.type_checker.is_optional(TestClass))
        self.assertFalse(self.type_checker.is_optional(List[str]))
        self.assertFalse(self.type_checker.is_optional(List[TestClass]))
        self.assertTrue(self.type_checker.is_optional(Optional[str]))
        self.assertTrue(self.type_checker.is_optional(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_optional(Type[str]))
        self.assertFalse(self.type_checker.is_optional(Type[TestClass]))
        self.assertTrue(self.type_checker.is_optional(Optional[List[Type[TestClass]]]))
        self.assertFalse(self.type_checker.is_optional(List[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_list(Set[TestClass]))
        self.assertFalse(self.type_checker.is_list(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_list(Named[TestClass]))
        self.assertFalse(self.type_checker.is_optional(Union[List[str], Tuple[str]]))

    def test_is_type(self):
        self.assertFalse(self.type_checker.is_type(str))
        self.assertFalse(self.type_checker.is_type(TestClass))
        self.assertFalse(self.type_checker.is_type(List[str]))
        self.assertFalse(self.type_checker.is_type(List[TestClass]))
        self.assertFalse(self.type_checker.is_type(Optional[str]))
        self.assertFalse(self.type_checker.is_type(Optional[TestClass]))
        self.assertTrue(self.type_checker.is_type(Type[str]))
        self.assertTrue(self.type_checker.is_type(Type[TestClass]))
        self.assertFalse(self.type_checker.is_type(Optional[List[Type[TestClass]]]))
        self.assertFalse(self.type_checker.is_type(List[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_list(Set[TestClass]))
        self.assertFalse(self.type_checker.is_list(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_list(Named[TestClass]))

    def test_is_set(self):
        self.assertFalse(self.type_checker.is_set(str))
        self.assertFalse(self.type_checker.is_set(TestClass))
        self.assertFalse(self.type_checker.is_set(List[str]))
        self.assertFalse(self.type_checker.is_set(List[TestClass]))
        self.assertFalse(self.type_checker.is_set(Optional[str]))
        self.assertFalse(self.type_checker.is_set(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_set(Type[str]))
        self.assertFalse(self.type_checker.is_set(Type[TestClass]))
        self.assertFalse(self.type_checker.is_set(Optional[List[Type[TestClass]]]))
        self.assertTrue(self.type_checker.is_set(Set[Type[TestClass]]))
        self.assertTrue(self.type_checker.is_set(Set[TestClass]))
        self.assertFalse(self.type_checker.is_set(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_set(Named[TestClass]))

    def test_is_tuple(self):
        self.assertFalse(self.type_checker.is_tuple(str))
        self.assertFalse(self.type_checker.is_tuple(TestClass))
        self.assertFalse(self.type_checker.is_tuple(List[str]))
        self.assertFalse(self.type_checker.is_tuple(List[TestClass]))
        self.assertFalse(self.type_checker.is_tuple(Optional[str]))
        self.assertFalse(self.type_checker.is_tuple(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_tuple(Type[str]))
        self.assertFalse(self.type_checker.is_tuple(Type[TestClass]))
        self.assertFalse(self.type_checker.is_tuple(Optional[List[Type[TestClass]]]))
        self.assertTrue(self.type_checker.is_tuple(Tuple[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_tuple(Set[TestClass]))
        self.assertTrue(self.type_checker.is_tuple(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_tuple(Named[TestClass]))

    def test_is_provider(self):
        self.assertFalse(self.type_checker.is_provider(str))
        self.assertFalse(self.type_checker.is_provider(TestClass))
        self.assertFalse(self.type_checker.is_provider(List[str]))
        self.assertFalse(self.type_checker.is_provider(List[TestClass]))
        self.assertFalse(self.type_checker.is_provider(Optional[str]))
        self.assertFalse(self.type_checker.is_provider(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_provider(Type[str]))
        self.assertFalse(self.type_checker.is_provider(Type[TestClass]))
        self.assertFalse(self.type_checker.is_provider(Optional[List[Type[TestClass]]]))
        self.assertFalse(self.type_checker.is_provider(Tuple[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_provider(Set[TestClass]))
        self.assertFalse(self.type_checker.is_provider(Tuple[TestClass]))
        self.assertFalse(self.type_checker.is_provider(Named[TestClass]))
        self.assertTrue(self.type_checker.is_provider(Provider[str]))
        self.assertTrue(self.type_checker.is_provider(Provider[TestClass]))

    def test_is_named(self):
        class MyNamedType(Named):
            original_type = str
            name = "my_name"

        self.assertFalse(self.type_checker.is_named(str))
        self.assertFalse(self.type_checker.is_named(TestClass))
        self.assertFalse(self.type_checker.is_named(List[str]))
        self.assertFalse(self.type_checker.is_named(List[TestClass]))
        self.assertFalse(self.type_checker.is_named(Optional[str]))
        self.assertFalse(self.type_checker.is_named(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_named(Type[str]))
        self.assertFalse(self.type_checker.is_named(Type[TestClass]))
        self.assertFalse(self.type_checker.is_named(Optional[List[Type[TestClass]]]))
        self.assertFalse(self.type_checker.is_named(Set[TestClass]))
        self.assertFalse(self.type_checker.is_named(Tuple[TestClass]))
        self.assertTrue(self.type_checker.is_named(MyNamedType))

    # pylint: disable=unsubscriptable-object
    @unittest.skipIf(not PEP_585, "Python 3.9 required")
    def test_pep85_style(self):
        self.assertTrue(self.type_checker.is_list(list[str]))
        self.assertFalse(self.type_checker.is_set(list[str]))
        self.assertFalse(self.type_checker.is_tuple(list[str]))
        self.assertFalse(self.type_checker.is_list(list))

        self.assertFalse(self.type_checker.is_list(set[str]))
        self.assertTrue(self.type_checker.is_set(set[str]))
        self.assertFalse(self.type_checker.is_tuple(set[str]))
        self.assertFalse(self.type_checker.is_set(set))

        self.assertFalse(self.type_checker.is_list(tuple[str]))
        self.assertFalse(self.type_checker.is_set(tuple[str]))
        self.assertTrue(self.type_checker.is_tuple(tuple[str]))
        self.assertFalse(self.type_checker.is_tuple(tuple))

        self.assertTrue(self.type_checker.is_type(type[str]))
        self.assertFalse(self.type_checker.is_type(type))
