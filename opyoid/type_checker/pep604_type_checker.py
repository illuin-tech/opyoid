import types
from typing import Type

from opyoid.type_checker.pep585_type_checker import Pep585TypeChecker


# noinspection PyUnresolvedReferences
class Pep604TypeChecker(Pep585TypeChecker):
    """Various helpers to check type hints."""

    @staticmethod
    def is_union(target_type: Type) -> bool:
        """Returns True if target_type is Union[<Any>, <Any>...] or Optional[<Any>] or <Any> | <Any>..."""
        # pylint: disable=no-member
        return Pep585TypeChecker.is_union(target_type) or isinstance(target_type, types.UnionType)
