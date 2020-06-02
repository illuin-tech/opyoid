import unittest

from illuin_inject import BindingSpec, Injector
from illuin_inject.bindings import InstanceBinding


class MyType:
    pass


class TestInjector(unittest.TestCase):
    def test_inject_from_binding(self):
        my_instance = MyType()
        injector = Injector(bindings=[
            InstanceBinding(MyType, my_instance)
        ])
        self.assertIs(my_instance, injector.inject(MyType))

    def test_inject_from_binding_spec(self):
        my_instance = MyType()

        class MyBindingSpec(BindingSpec):
            def configure(self) -> None:
                self.bind(MyType, to_instance=my_instance)

        injector = Injector([MyBindingSpec()])
        self.assertEqual(my_instance, injector.inject(MyType))

    def test_inject_from_multiple_providers_takes_last(self):
        my_instance = MyType()
        my_instance_2 = MyType()
        injector = Injector(bindings=[
            InstanceBinding(MyType, my_instance),
            InstanceBinding(MyType, my_instance_2),
        ])
        self.assertIs(my_instance_2, injector.inject(MyType))
