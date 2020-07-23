import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, PerLookupScope, SingletonScope, ThreadScope, \
    annotated_arg
from illuin_inject.bindings import ClassBindingToProviderAdapter, FromClassProvider
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.provider import Provider
from illuin_inject.providers import ProviderCreator
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider
from illuin_inject.target import Target


class MyType:
    def __init__(self):
        pass


class TestClassBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ClassBindingToProviderAdapter()
        self.provider_creator = create_autospec(ProviderCreator, spec_set=True)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_accept_class_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(ClassBinding(MyType)))

    def test_accept_non_class_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType())))
        self.assertFalse(self.adapter.accept(FactoryBinding(MyType, create_autospec(Factory))))

    def test_create_provider_without_args(self):
        self.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(ClassBinding(MyType), self.provider_creator)

        self.provider_creator.get_provider.assert_called_once_with(
            Target(SingletonScope),
        )
        self.assertIsInstance(provider, FromClassProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_scoped_provider(self):
        mock_scope_provider = create_autospec(Provider, spec_set=True)
        mock_scope_provider.get.return_value = ThreadScope()
        self.provider_creator.get_provider.return_value = mock_scope_provider
        provider = self.adapter.create(ClassBinding(MyType, scope=ThreadScope), self.provider_creator)

        self.provider_creator.get_provider.assert_called_once_with(Target(ThreadScope))

        self.assertIsInstance(provider, ThreadScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_parameters(self):
        class MyOtherType:
            def __init__(self, arg_1: str, arg_2: int, *args, arg_3: float, **kwargs):
                self.args = [arg_1, arg_2, *args]
                self.kwargs = {
                    "arg_3": arg_3,
                    **kwargs,
                }

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"
        mock_provider_2 = create_autospec(Provider)
        mock_provider_2.get.return_value = 2
        mock_provider_3 = create_autospec(Provider)
        mock_provider_3.get.return_value = 3.4

        self.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            mock_provider_2,
            mock_provider_3,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(["my_arg_1", 2], instance.args)
        self.assertEqual({"arg_3": 3.4}, instance.kwargs)
        self.assertEqual([
            call(Target(str)),
            call(Target(int)),
            call(Target(float)),
            call(Target(SingletonScope)),
        ], self.provider_creator.get_provider.call_args_list)

    def test_create_provider_from_annotated_binding(self):
        class MyOtherType:
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType, annotation="my_annotation"), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str)),
            call(Target(SingletonScope)),
        ], self.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_annotated_args(self):
        class MyOtherType:
            @annotated_arg("arg", "my_annotation")
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str, "my_annotation")),
            call(Target(SingletonScope)),
        ], self.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_missing_parameters_raises_exception(self):
        class MyOtherType:
            def __init__(self, arg: str) -> None:
                self.arg = arg

            self.provider_creator.get_provider.side_effect = NoBindingFound

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(ClassBinding(MyOtherType), self.provider_creator)

    def test_create_provider_with_default_parameter(self):
        class MyOtherType:
            def __init__(self, arg: str = "default_value") -> None:
                self.arg = arg

        self.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.provider_creator)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_without_type_hint(self):
        class MyOtherType:
            def __init__(self, arg="default_value") -> None:
                self.arg = arg

        self.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.provider_creator)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_with_subclass(self):
        class MyOtherType(MyType):
            def __init__(self, arg: str):
                MyType.__init__(self)
                self.arg = arg

        mock_provider = create_autospec(Provider)
        mock_provider.get.return_value = "my_arg_1"

        self.provider_creator.get_provider.side_effect = [
            mock_provider,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(ClassBinding(MyType, MyOtherType), self.provider_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)

    def test_non_injectable_scope_raises_exception(self):
        self.provider_creator.get_provider.side_effect = NoBindingFound()

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(ClassBinding(MyType), self.provider_creator)
