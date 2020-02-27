from typing import GenericMeta, List, Set, Tuple, Type, Union

from .annotated import Annotated


# noinspection PyUnresolvedReferences
class TypeChecker:
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
    def is_annotated(target_type: Type) -> bool:
        """Returns True if target_type is Annotated[<Any>]"""
        return issubclass(target_type, Annotated)

    @staticmethod
    def is_optional(target_type: Type) -> bool:
        """Returns True if target_type is Optional[<Any>]"""
        return hasattr(target_type, "__origin__") \
               and target_type.__origin__ == Union \
               and len(target_type.__args__) == 2 \
               and isinstance(None, target_type.__args__[1])

    @staticmethod
    def is_type(target_type: Type) -> bool:
        """Returns True if target_type is Type[<Any>]"""
        return isinstance(target_type, GenericMeta) and target_type.__origin__ == Type
