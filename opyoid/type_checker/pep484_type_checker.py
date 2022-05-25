# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import GenericMeta, List, Set, Tuple, Type, Union, _Union

from opyoid.named import Named
from opyoid.provider import Provider


# noinspection PyUnresolvedReferences
class Pep484TypeChecker:
    """Various helpers to check type hints."""

    @staticmethod
    def is_list(target_type: Type) -> bool:
        """Returns True if target_type is List[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == List

    @staticmethod
    def is_set(target_type: Type) -> bool:
        """Returns True if target_type is Set[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Set

    @staticmethod
    def is_tuple(target_type: Type) -> bool:
        """Returns True if target_type is Tuple[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Tuple

    @staticmethod
    def is_provider(target_type: Type) -> bool:
        """Returns True if target_type is Provider[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Provider

    @staticmethod
    def is_named(target_type: Type) -> bool:
        """Returns True if target_type is Named[<Any>]"""
        return isinstance(target_type, type) and issubclass(target_type, Named)

    @staticmethod
    def is_union(target_type: Type) -> bool:
        """Returns True if target_type is Union[<Any>, <Any>...] or Optional[<Any>]"""
        # pylint: disable=comparison-with-callable
        return isinstance(target_type, _Union) and target_type.__origin__ == Union

    @staticmethod
    def is_type(target_type: Type) -> bool:
        """Returns True if target_type is Type[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Type
