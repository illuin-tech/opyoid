import unittest
from inspect import signature

from opyoid.annotated import Annotated, annotated_arg
from opyoid.exceptions import AnnotationError


class MyType:
    pass


class MyOtherType:
    pass


class TestAnnotated(unittest.TestCase):
    def setUp(self) -> None:
        self.annotated = Annotated()

    def test_annotated_arg_replaces_type(self):
        class MyClass:
            @annotated_arg("my_param", "my_annotation")
            def __init__(self, my_param: MyType, my_other_param: MyOtherType):
                pass

        parameters = signature(MyClass.__init__).parameters
        my_param = parameters["my_param"]
        self.assertTrue(issubclass(my_param.annotation, Annotated))
        self.assertEqual(MyType, my_param.annotation.original_type)
        self.assertEqual("my_annotation", my_param.annotation.annotation)
        self.assertEqual(MyOtherType, parameters["my_other_param"].annotation)

    def test_default_is_preserved(self):
        class MyClass:
            @annotated_arg("my_param", "my_annotation")
            def __init__(self, my_param: int = 3):
                pass

        parameters = signature(MyClass.__init__).parameters
        my_param = parameters["my_param"]
        self.assertTrue(issubclass(my_param.annotation, Annotated))
        self.assertEqual(int, my_param.annotation.original_type)
        self.assertEqual("my_annotation", my_param.annotation.annotation)
        self.assertEqual(3, my_param.default)

    def test_adding_annotation_on_unknown_parameter_raises_exception(self):
        # pylint: disable=unused-variable
        with self.assertRaises(AnnotationError):
            class MyClass:
                @annotated_arg("my_unknown_arg", "my_annotation")
                def __init__(self, my_param: MyType):
                    pass

    def test_adding_annotation_on_untyped_parameter_raises_exception(self):
        # pylint: disable=unused-variable
        with self.assertRaises(AnnotationError):
            class MyClass:
                @annotated_arg("my_param", "my_annotation")
                def __init__(self, my_param):
                    pass
