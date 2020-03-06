import unittest
from typing import List, Optional, Type, Set, Tuple

from illuin_inject.annotated import Annotated
from illuin_inject.type_checker import TypeChecker


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
        self.assertFalse(self.type_checker.is_list(Annotated[TestClass]))

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
        self.assertFalse(self.type_checker.is_list(Annotated[TestClass]))

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
        self.assertFalse(self.type_checker.is_list(Annotated[TestClass]))

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
        self.assertFalse(self.type_checker.is_set(Annotated[TestClass]))

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
        self.assertFalse(self.type_checker.is_tuple(Annotated[TestClass]))

    def test_is_annotated(self):
        class MyAnnotatedType(Annotated):
            original_type = str
            annotation = "my_annotation"

        self.assertFalse(self.type_checker.is_annotated(str))
        self.assertFalse(self.type_checker.is_annotated(TestClass))
        self.assertFalse(self.type_checker.is_annotated(List[str]))
        self.assertFalse(self.type_checker.is_annotated(List[TestClass]))
        self.assertFalse(self.type_checker.is_annotated(Optional[str]))
        self.assertFalse(self.type_checker.is_annotated(Optional[TestClass]))
        self.assertFalse(self.type_checker.is_annotated(Type[str]))
        self.assertFalse(self.type_checker.is_annotated(Type[TestClass]))
        self.assertFalse(self.type_checker.is_annotated(Optional[List[Type[TestClass]]]))
        self.assertTrue(self.type_checker.is_annotated(Annotated[Type[TestClass]]))
        self.assertFalse(self.type_checker.is_annotated(Set[TestClass]))
        self.assertFalse(self.type_checker.is_annotated(Tuple[TestClass]))
        self.assertTrue(self.type_checker.is_annotated(Annotated[TestClass]))
        self.assertTrue(self.type_checker.is_annotated(MyAnnotatedType))
