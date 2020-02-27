import sys

from .annotated import Annotated

NEW_TYPING = sys.version_info[:3] >= (3, 7, 0)  # PEP 560
# pylint: disable=no-name-in-module
if NEW_TYPING:  # pragma: nocover
    from typing import _GenericAlias, Type, Union
else:  # pragma: nocover
    from typing import GenericMeta, List, Set, Tuple, Type, Union, _Union


# noinspection PyUnresolvedReferences
class TypeChecker:  # pragma: nocover
    @staticmethod
    def is_list(target_type: Type) -> bool:
        """Returns True if target_type is List[<Any>]"""
        if NEW_TYPING:
            return isinstance(target_type, _GenericAlias) and target_type.__origin__ == list
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == List

    @staticmethod
    def is_set(target_type: Type) -> bool:
        """Returns True if target_type is Set[<Any>]"""
        if NEW_TYPING:
            return isinstance(target_type, _GenericAlias) and target_type.__origin__ == set
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Set

    @staticmethod
    def is_tuple(target_type: Type) -> bool:
        """Returns True if target_type is Tuple[<Any>]"""
        if NEW_TYPING:
            return isinstance(target_type, _GenericAlias) and target_type.__origin__ == tuple
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Tuple

    @staticmethod
    def is_annotated(target_type: Type) -> bool:
        """Returns True if target_type is Annotated[<Any>]"""
        return isinstance(target_type, type) and issubclass(target_type, Annotated)

    @staticmethod
    def is_optional(target_type: Type) -> bool:
        """Returns True if target_type is Optional[<Any>]"""
        if NEW_TYPING:
            return isinstance(target_type, _GenericAlias) \
                   and target_type.__origin__ == Union \
                   and len(target_type.__args__) >= 2 \
                   and isinstance(None, target_type.__args__[-1])
        return isinstance(target_type, _Union) \
               and target_type.__origin__ == Union \
               and len(target_type.__args__) >= 2 \
               and isinstance(None, target_type.__args__[-1])

    @staticmethod
    def is_type(target_type: Type) -> bool:
        """Returns True if target_type is Type[<Any>]"""
        if NEW_TYPING:
            return isinstance(target_type, _GenericAlias) and target_type.__origin__ == type
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Type
