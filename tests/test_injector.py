import unittest

from opyoid import Injector, Module
from opyoid.bindings import InstanceBinding


class MyType:
    pass


class TestInjector(unittest.TestCase):
    def test_inject_from_binding(self):
        my_instance = MyType()
        injector = Injector(bindings=[InstanceBinding(MyType, my_instance)])
        self.assertIs(my_instance, injector.inject(MyType))

    def test_inject_from_module(self):
        my_instance = MyType()

        class MyModule(Module):
            def configure(self) -> None:
                self.bind(MyType, to_instance=my_instance)

        injector = Injector([MyModule()])
        self.assertEqual(my_instance, injector.inject(MyType))

    def test_inject_from_multiple_providers_takes_last(self):
        my_instance = MyType()
        my_instance_2 = MyType()
        injector = Injector(
            bindings=[
                InstanceBinding(MyType, my_instance),
                InstanceBinding(MyType, my_instance_2),
            ]
        )
        self.assertIs(my_instance_2, injector.inject(MyType))
