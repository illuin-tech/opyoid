import unittest
from typing import Generic, List, TypeVar

from opyoid.named import Named
from opyoid.utils import get_class_full_name


class MyClass:
    pass


GenericT = TypeVar("GenericT")


class MyGenericClass(Generic[GenericT]):
    pass


class TestUtils(unittest.TestCase):
    def test_get_class_full_name(self):
        self.assertTrue(get_class_full_name(MyClass).endswith("test_utils.MyClass"))

    def test_get_builtin_class_full_name(self):
        self.assertEqual("int", get_class_full_name(int))

    def test_get_generic_builtin_class_full_name(self):
        self.assertEqual("typing.List[int]", get_class_full_name(List[int]))

    def test_get_generic_class_full_name(self):
        self.assertTrue(get_class_full_name(MyGenericClass[int]).endswith("test_utils.MyGenericClass[int]"))

    def test_get_named_class_full_name(self):
        self.assertEqual("int#my_name", get_class_full_name(Named.get_named_class(int, "my_name")))

    def test_str_get_class_full_name(self):
        self.assertEqual("MyClass", get_class_full_name("MyClass"))
