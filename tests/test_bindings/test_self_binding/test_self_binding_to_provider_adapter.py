import unittest
from inspect import signature
from typing import List
from unittest.mock import call, create_autospec

from opyoid import (
    AbstractModule,
    InstanceBinding,
    named_arg,
    PerLookupScope,
    Provider,
    SelfBinding,
    SingletonScope,
    ThreadScope,
)
from opyoid.bindings import BindingRegistry, FromCallableProvider, SelfBindingToProviderAdapter
from opyoid.bindings.registered_binding import RegisteredBinding
from opyoid.exceptions import IncompatibleAdapter, NoBindingFound, NonInjectableTypeError
from opyoid.injection_context import InjectionContext
from opyoid.injection_state import InjectionState
from opyoid.providers import ProviderCreator
from opyoid.scopes.thread_scoped_provider import ThreadScopedProvider
from opyoid.target import Target


class MyType:
    pass


# mypy: disable-error-code="attr-defined"
class TestSelfBindingToProviderAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = SelfBindingToProviderAdapter()
        self.state = InjectionState(
            create_autospec(ProviderCreator, spec_set=True),
            create_autospec(BindingRegistry, spec_set=True),
        )
        self.context = InjectionContext(Target(MyType), self.state)
        self.mock_scope_provider = create_autospec(Provider, spec_set=True)
        self.scope = PerLookupScope()
        self.mock_scope_provider.get.return_value = self.scope
        self.module = create_autospec(AbstractModule, spec_set=True)

    def test_create_provider_without_args(self):
        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyType), self.module), self.context)

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(SingletonScope)),
        )
        self.assertIsInstance(provider, FromCallableProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyType)

    def test_create_provider_with_default_constructor(self):
        class MyOtherType:
            pass

        self.state.provider_creator.get_provider.return_value = self.mock_scope_provider

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(SingletonScope)),
        )
        self.assertIsInstance(provider, FromCallableProvider)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)

    def test_create_scoped_provider(self):
        mock_scope_provider = create_autospec(Provider, spec_set=True)
        mock_scope_provider.get.return_value = ThreadScope()
        self.state.provider_creator.get_provider.return_value = mock_scope_provider
        provider = self.adapter.create(
            RegisteredBinding(SelfBinding(MyType, scope=ThreadScope), self.module), self.context
        )

        self.state.provider_creator.get_provider.assert_called_once_with(
            self.context.get_child_context(Target(ThreadScope))
        )

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

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(["my_arg_1", 2, 1.2, 3.4], instance.args)
        self.assertEqual({"arg_3": True}, instance.kwargs)
        ctx_1 = self.context.get_child_context(Target(str, "arg_1"), allow_jit_provider=False)
        ctx_1.current_class = MyOtherType
        ctx_1.current_parameter = signature(MyOtherType).parameters.get("arg_1")
        ctx_2 = self.context.get_child_context(Target(int, "arg_2"), allow_jit_provider=False)
        ctx_2.current_class = MyOtherType
        ctx_2.current_parameter = signature(MyOtherType).parameters.get("arg_2")
        ctx_3 = self.context.get_child_context(Target(List[float], "args"), allow_jit_provider=False)
        ctx_3.current_class = MyOtherType
        ctx_3.current_parameter = signature(MyOtherType).parameters.get("args")
        ctx_4 = self.context.get_child_context(Target(bool, "arg_3"), allow_jit_provider=False)
        ctx_4.current_class = MyOtherType
        ctx_4.current_parameter = signature(MyOtherType).parameters.get("arg_3")
        ctx_5 = self.context.get_child_context(Target(SingletonScope), allow_jit_provider=True)

        self.assertEqual(
            [
                call(ctx_1),
                call(ctx_2),
                call(ctx_3),
                call(ctx_4),
                call(ctx_5),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )

    def test_create_provider_from_named_binding(self):
        class MyOtherType:
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(
            RegisteredBinding(SelfBinding(MyOtherType, named="my_name"), self.module), self.context
        )
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        ctx_1 = self.context.get_child_context(Target(str, "arg"), allow_jit_provider=False)
        ctx_1.current_class = MyOtherType
        ctx_1.current_parameter = signature(MyOtherType).parameters.get("arg")
        ctx_2 = self.context.get_child_context(Target(str), allow_jit_provider=True)
        ctx_2.current_class = MyOtherType
        ctx_2.current_parameter = signature(MyOtherType).parameters.get("arg")
        ctx_3 = self.context.get_child_context(Target(SingletonScope), allow_jit_provider=True)
        self.assertEqual(
            [
                call(ctx_1),
                call(ctx_2),
                call(ctx_3),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )

    def test_create_provider_with_named_positional_argument(self):
        class MyOtherType:
            @named_arg("arg", "my_name")
            def __init__(self, arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = "my_arg_1"

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual("my_arg_1", instance.arg)
        ctx_1 = self.context.get_child_context(Target(str, "my_name"), allow_jit_provider=True)
        ctx_1.current_class = MyOtherType
        ctx_1.current_parameter = signature(MyOtherType).parameters.get("arg")
        ctx_2 = self.context.get_child_context(Target(SingletonScope), allow_jit_provider=True)
        self.assertEqual(
            [
                call(ctx_1),
                call(ctx_2),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )

    def test_create_provider_with_named_args(self):
        class MyOtherType:
            @named_arg("arg", "my_name")
            def __init__(self, *arg: str):
                self.arg = arg

        mock_provider_1 = create_autospec(Provider)
        mock_provider_1.get.return_value = ["my_arg_1"]

        self.state.provider_creator.get_provider.side_effect = [
            mock_provider_1,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)
        instance = provider.get()
        self.assertIsInstance(instance, MyOtherType)
        self.assertEqual(("my_arg_1",), instance.arg)
        ctx_1 = self.context.get_child_context(Target(List[str], "my_name"), allow_jit_provider=True)
        ctx_1.current_class = MyOtherType
        ctx_1.current_parameter = signature(MyOtherType).parameters.get("arg")
        ctx_2 = self.context.get_child_context(Target(SingletonScope), allow_jit_provider=True)

        self.assertEqual(
            [
                call(ctx_1),
                call(ctx_2),
            ],
            self.state.provider_creator.get_provider.call_args_list,
        )

    def test_create_provider_with_missing_parameters_raises_exception(self):
        class MyOtherType:
            def __init__(self, arg: str) -> None:
                self.arg = arg

            self.state.provider_creator.get_provider.side_effect = NoBindingFound

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)

    def test_create_provider_with_default_parameter(self):
        class MyOtherType:
            def __init__(self, arg: str = "default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            NoBindingFound,
            NoBindingFound,
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_create_provider_without_type_hint(self):
        class MyOtherType:
            def __init__(self, arg="default_value") -> None:
                self.arg = arg

        self.state.provider_creator.get_provider.side_effect = [
            self.mock_scope_provider,
        ]

        provider = self.adapter.create(RegisteredBinding(SelfBinding(MyOtherType), self.module), self.context)
        instance = provider.get()
        self.assertEqual(instance.arg, "default_value")

    def test_non_injectable_scope_raises_exception(self):
        self.state.provider_creator.get_provider.side_effect = NoBindingFound()

        with self.assertRaises(NonInjectableTypeError):
            self.adapter.create(RegisteredBinding(SelfBinding(MyType), self.module), self.context)

    def test_other_binding_type_raises_exception(self):
        with self.assertRaises(IncompatibleAdapter):
            self.adapter.create(RegisteredBinding(InstanceBinding(MyType, MyType()), self.module), self.context)
