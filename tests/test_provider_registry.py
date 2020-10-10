import unittest
from unittest.mock import create_autospec

from opyoid import NonInjectableTypeError, Provider, Target
from opyoid.provider_registry import ProviderRegistry


class MyType:
    pass


class MyOtherType:
    pass


class TestProviderRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = ProviderRegistry()
        self.target = Target(MyType)
        self.annotated_target = Target(MyType, "my_annotation")
        self.other_target = Target(MyOtherType)
        self.provider_1 = create_autospec(Provider, spec_set=True)
        self.provider_2 = create_autospec(Provider, spec_set=True)
        self.provider_3 = create_autospec(Provider, spec_set=True)

    def test_register_saves_provider_to_new_type(self):
        self.registry.set_provider(self.target, self.provider_1)
        self.registry.set_provider(self.annotated_target, self.provider_2)
        self.registry.set_provider(self.other_target, self.provider_3)
        self.assertEqual(self.provider_1, self.registry.get_provider(self.target))
        self.assertEqual(self.provider_2, self.registry.get_provider(self.annotated_target))
        self.assertEqual(self.provider_3, self.registry.get_provider(self.other_target))

    def test_get_provider_for_unknown_type_returns_none(self):
        provider = self.registry.get_provider(self.target)
        self.assertIsNone(provider)

    def test_get_provider_from_string_type(self):
        self.registry.set_provider(self.target, self.provider_1)
        self.registry.set_provider(self.annotated_target, self.provider_2)
        provider = self.registry.get_provider(Target("MyType"))

        self.assertEqual(self.provider_1, provider)

    def test_get_annotated_provider_from_string(self):
        self.registry.set_provider(self.target, self.provider_1)
        self.registry.set_provider(self.annotated_target, self.provider_2)
        provider = self.registry.get_provider(Target("MyType", "my_annotation"))

        self.assertEqual(self.provider_2, provider)

    def test_get_provider_from_unknown_string(self):
        provider = self.registry.get_provider(Target("MyUnknownType"))
        self.assertIsNone(provider)

    def test_get_provider_from_string_with_name_conflict_raises_exception(self):
        class MyNewType:
            pass

        target_1 = Target(MyNewType)

        # pylint: disable=function-redefined
        class MyNewType:
            pass

        target_2 = Target(MyNewType)

        self.registry.set_provider(target_1, self.provider_1)
        self.registry.set_provider(target_2, self.provider_2)

        with self.assertRaises(NonInjectableTypeError):
            self.registry.get_provider(Target("MyNewType"))
