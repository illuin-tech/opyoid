import unittest
from typing import List, Optional, Type

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
