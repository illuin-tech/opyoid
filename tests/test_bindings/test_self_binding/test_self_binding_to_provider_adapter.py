import unittest
from typing import List
from unittest.mock import call, create_autospec

from illuin_inject import ClassBinding, InstanceBinding, PerLookupScope, Provider, ProviderBinding, SelfBinding, \
    SingletonScope, ThreadScope, annotated_arg
from illuin_inject.bindings import BindingRegistry, FromClassProvider, SelfBindingToProviderAdapter
from illuin_inject.exceptions import NoBindingFound, NonInjectableTypeError
from illuin_inject.injection_state import InjectionState
from illuin_inject.providers import ProviderCreator
from illuin_inject.scopes.thread_scoped_provider import ThreadScopedProvider
from illuin_inject.target import Target


class MyType:
    def __init__(self):
        pass


class TestSelfBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SelfBindingToProviderAdapter()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope

    def test_accept_self_binding_returns_true(self):
        self.assertTrue(self.adapter.accept(SelfBinding(MyType), self.state))

    def test_accept_non_self_binding_returns_false(self):
        self.assertFalse(self.adapter.accept(InstanceBinding(MyType, MyType()), self.state))
        self.assertFalse(self.adapter.accept(ClassBinding(MyType, MyType), self.state))
        self.assertFalse(self.adapter.accept(ProviderBinding(MyType, create_autospec(Provider)), self.state))

    def test_create_provider_without_args(self):
        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(SelfBinding(MyType), self.state)

        self.state.provider_creator.get_provider.assert_called_once_with(
            Target(SingletonScope),
            self.state,
        )
        self.assertIsInstance(provider, FromClassProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_default_constructor(self):
        class MyOtherType:
            pass

        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)

        self.state.provider_creator.get_provider.assert_called_once_with(
            Target(SingletonScope),
            self.state,
        )
        self.assertIsInstance(provider, FromClassProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)

    def test_create_scoped_provider(self):
        mock_scope_provider = create_autospec(Provider, spec_set=True)
        mock_scope_provider.get.return_value = ThreadScope()
        self.state.provider_creator.get_provider.return_value = mock_scope_provider
        provider = self.adapter.create(SelfBinding(MyType, scope=ThreadScope), self.state)

        self.state.provider_creator.get_provider.assert_called_once_with(Target(ThreadScope), self.state)

        self.assertIsInstance(provider, ThreadScopedProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_parameters(self):
        class MyOtherType:
            def __init__(self, arg_1: str, arg_2: int, *args: float, arg_3: bool, **kwargs):
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
        mock_provider_3.get.return_value = [1.2, 3.4]
        mock_provider_4 = create_autospec(Provider)
        mock_provider_4.get.return_value = True

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            mock_provider_2,
            mock_provider_3,
            mock_provider_4,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(["my_arg_1", 2, 1.2, 3.4], instance.args)
        self.assertEqual({"arg_3": True}, instance.kwargs)
        self.assertEqual([
            call(Target(str), self.state),
            call(Target(int), self.state),
            call(Target(List[float]), self.state),
            call(Target(bool), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_from_annotated_binding(self):
        class MyOtherType:
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType, annotation="my_annotation"), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_annotated_positional_argument(self):
        class MyOtherType:
            @annotated_arg("arg", "my_annotation")
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        self.assertEqual([
            call(Target(str, "my_annotation"), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_annotated_args(self):
        class MyOtherType:
            @annotated_arg("arg", "my_annotation")
            def __init__(self, *arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = ["my_arg_1"]

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(("my_arg_1",), instance.arg)
        self.assertEqual([
            call(Target(List[str], "my_annotation"), self.state),
            call(Target(SingletonScope), self.state),
        ], self.state.provider_creator.get_provider.call_args_list)

    def test_create_provider_with_missing_parameters_raises_exception(self):
        class MyOtherType:
            def __init__(self, arg: str) -> None:
                self.arg = arg

            self.state.provider_creator.get_provider.side_effect = NoBindingFound

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(SelfBinding(MyOtherType), self.state)

    def test_create_provider_with_default_parameter(self):
        class MyOtherType:
            def __init__(self, arg: str = "default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_without_type_hint(self):
        class MyOtherType:
            def __init__(self, arg="default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(SelfBinding(MyOtherType), self.state)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_non_injectable_scope_raises_exception(self):
        self.state.provider_creator.get_provider.side_effect = NoBindingFound()

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(SelfBinding(MyType), self.state)
