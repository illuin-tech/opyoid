# pylint: disable=no-name-in-module
# noinspection PyUnresolvedReferences
from types import GenericAlias  # type: ignore[attr-defined]
from typing import Any

from opyoid.type_checker.pep560_type_checker import Pep560TypeChecker


class Pep585TypeChecker(Pep560TypeChecker):
    """Various helpers to check type hints."""

    @staticmethod
    def is_list(target_type: Any) -> bool:
        """Returns True if target_type is List[<Any>] or list[<Any>]"""
        return Pep560TypeChecker.is_list(target_type) or (
            isinstance(target_type, GenericAlias) and target_type.__origin__ == list
        )

    @staticmethod
    def is_set(target_type: Any) -> bool:
        """Returns True if target_type is Set[<Any>] or set[<Any>]"""
        return Pep560TypeChecker.is_set(target_type) or (
            isinstance(target_type, GenericAlias) and target_type.__origin__ == set
        )

    @staticmethod
    def is_tuple(target_type: Any) -> bool:
        """Returns True if target_type is Tuple[<Any>] or tuple[<Any>]"""
        return Pep560TypeChecker.is_tuple(target_type) or (
            isinstance(target_type, GenericAlias) and target_type.__origin__ == tuple
        )

    @staticmethod
    def is_type(target_type: Any) -> bool:
        """Returns True if target_type is Type[<Any>]"""
        return Pep560TypeChecker.is_type(target_type) or (
            isinstance(target_type, GenericAlias) and target_type.__origin__ == type
        )
