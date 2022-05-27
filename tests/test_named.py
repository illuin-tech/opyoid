import unittest
from inspect import signature

from opyoid.exceptions import NamedError
from opyoid.named import Named, named_arg


class MyType:
    pass


class MyOtherType:
    pass


class TestNamed(unittest.TestCase):
    def setUp(self) -> None:
        self.named = Named()

    def test_named_arg_replaces_type(self):
        class MyClass:
            @named_arg("my_param", "my_name")
            def __init__(self, my_param: MyType, my_other_param: MyOtherType):
                self.my_param = my_param
                self.my_other_param = my_other_param

        parameters = signature(MyClass.__init__).parameters
        my_param = parameters["my_param"]
        self.assertTrue(issubclass(my_param.annotation, Named))
        self.assertEqual(MyType, my_param.annotation.original_type)
        self.assertEqual("my_name", my_param.annotation.name)
        self.assertEqual(MyOtherType, parameters["my_other_param"].annotation)

    def test_default_is_preserved(self):
        class MyClass:
            @named_arg("my_param", "my_name")
            def __init__(self, my_param: int = 3):
                self.my_param = my_param

        parameters = signature(MyClass.__init__).parameters
        my_param = parameters["my_param"]
        self.assertTrue(issubclass(my_param.annotation, Named))
        self.assertEqual(int, my_param.annotation.original_type)
        self.assertEqual("my_name", my_param.annotation.name)
        self.assertEqual(3, my_param.default)

    def test_adding_name_on_unknown_parameter_raises_exception(self):
        # pylint: disable=unused-variable
        with self.assertRaises(NamedError):

            class MyClass:
                @named_arg("my_unknown_arg", "my_name")
                def __init__(self, my_param: MyType):
                    self.my_param = my_param

    def test_adding_name_on_untyped_parameter_raises_exception(self):
        # pylint: disable=unused-variable
        with self.assertRaises(NamedError):

            class MyClass:
                @named_arg("my_param", "my_name")
                def __init__(self, my_param):
                    self.my_param = my_param
