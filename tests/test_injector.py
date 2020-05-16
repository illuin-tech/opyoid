import unittest
from unittest.mock import create_autospec

from illuin_inject import BindingSpec, ClassBinding, ImmediateScope, Injector, SingletonScope
from illuin_inject.bindings import FactoryBinding, InstanceBinding
from illuin_inject.factory import Factory


class MyType:
    pass


class TestInjector(unittest.TestCase):
    def test_inject_from_binding(self):
        my_instance = MyType()
        injector = Injector(bindings=[
            InstanceBinding(MyType, my_instance)
        ])
        self.assertEqual(my_instance, injector.inject(MyType))

    def test_inject_from_binding_spec(self):
        my_instance = MyType()

        class MyBindingSpec(BindingSpec):
            def configure(self) -> None:
                self.bind(MyType, to_instance=my_instance)

        injector = Injector([MyBindingSpec()])
        self.assertEqual(my_instance, injector.inject(MyType))

    def test_immediate_scoped_bindings_are_injected(self):
        mocked_class_1 = create_autospec(MyType, spec_set=True)
        mocked_class_2 = create_autospec(MyType, spec_set=True)
        mocked_class_3 = create_autospec(MyType, spec_set=True)
        mocked_class_4 = create_autospec(MyType, spec_set=True)

        class MyFactory1(Factory[MyType]):
            def create(self) -> MyType:
                return mocked_class_3()

        class MyFactory2(Factory[MyType]):
            def create(self) -> MyType:
                return mocked_class_4()

        Injector(
            bindings=[
                ClassBinding(mocked_class_1, scope=ImmediateScope),
                ClassBinding(mocked_class_2, scope=SingletonScope),
                FactoryBinding(mocked_class_3, MyFactory1, scope=ImmediateScope),
                FactoryBinding(mocked_class_4, MyFactory2, scope=SingletonScope),
            ]
        )
        mocked_class_1.assert_called_once_with()
        mocked_class_2.assert_not_called()
        mocked_class_3.assert_called_once_with()
        mocked_class_4.assert_not_called()
