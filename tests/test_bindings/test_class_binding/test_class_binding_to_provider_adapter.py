import unittest
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, FactoryBinding, InstanceBinding, ThreadScope, annotated_arg
from illuin_inject.bindings import ClassBindingToProviderAdapter
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.factory import Factory
from illuin_inject.provider import Provider
from illuin_inject.providers import ProvidersCreator
from illuin_inject.scopes.singleton_scoped_provider import SingletonScopedProvider
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider
from illuin_inject.target import Target


class MyType:
    def __init__(self):
        pass


class TestClassBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ClassBindingToProviderAdapter()
        self.providers_creator = create_autospec(ProvidersCreator, spec_set=True)

    def test_accept_class_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(ClassBinding(MyType)))

    def test_accept_non_class_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType())))
        self.assertFalse(self.adapter.accept(FactoryBinding(MyType, create_autospec(Factory))))

    def test_create_provider_without_args(self):
        provider = self.adapter.create(ClassBinding(MyType), self.providers_creator)
        self.providers_creator.get_providers.assert_not_called()

        self.assertIsInstance(provider, SingletonScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_scoped_provider(self):
        provider = self.adapter.create(ClassBinding(MyType, scope=ThreadScope), self.providers_creator)
        self.providers_creator.get_providers.assert_not_called()

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
        mock_provider_4 = create_autospec(Provider)
        mock_provider_4.get.return_value = "unused_provider"

        self.providers_creator.get_providers.side_effect = [
            [
                mock_provider_4,
                mock_provider_1,
            ],
            [
                mock_provider_2,
            ],
            [
                mock_provider_3,
            ],
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.providers_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(["my_arg_1", 2], instance.args)
        self.assertEqual({"arg_3": 3.4}, instance.kwargs)
        self.assertEqual([
            call(Target(str)),
            call(Target(int)),
            call(Target(float)),
        ], self.providers_creator.get_providers.call_args_list)

    def test_create_provider_from_annotated_binding(self):
        class MyOtherType:
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.providers_creator.get_providers.side_effect = [
            [
                mock_provider_1,
            ],
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType, annotation="my_annotation"), self.providers_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str)),
        ], self.providers_creator.get_providers.call_args_list)

    def test_create_provider_with_annotated_args(self):
        class MyOtherType:
            @annotated_arg("arg", "my_annotation")
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.providers_creator.get_providers.side_effect = [
            [
                mock_provider_1,
            ],
        ]

        provider = self.adapter.create(ClassBinding(MyOtherType), self.providers_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str, "my_annotation")),
        ], self.providers_creator.get_providers.call_args_list)

    def test_create_provider_with_missing_parameters_raises_exception(self):
        class MyOtherType:
            def __init__(self, arg: str) -> None:
                self.arg = arg

            self.providers_creator.get_providers.side_effect = NoBindingFound

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(ClassBinding(MyOtherType), self.providers_creator)

    def test_create_provider_with_default_parameter(self):
        class MyOtherType:
            def __init__(self, arg: str = "default_value") -> None:
                self.arg = arg

            self.providers_creator.get_providers.side_effect = NoBindingFound

        provider = self.adapter.create(ClassBinding(MyOtherType), self.providers_creator)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_without_type_hint(self):
        class MyOtherType:
            def __init__(self, arg="default_value") -> None:
                self.arg = arg

            self.providers_creator.get_providers.side_effect = NoBindingFound

        provider = self.adapter.create(ClassBinding(MyOtherType), self.providers_creator)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_with_subclass(self):
        class MyOtherType(MyType):
            def __init__(self, arg: str):
                MyType.__init__(self)
                self.arg = arg

        mock_provider = create_autospec(Provider)
        mock_provider.get.return_value = "my_arg_1"

        self.providers_creator.get_providers.return_value = [mock_provider]

        provider = self.adapter.create(ClassBinding(MyType, MyOtherType), self.providers_creator)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
