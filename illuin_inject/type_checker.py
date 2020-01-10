from typing import GenericMeta, List, Type, Union


# noinspection PyUnresolvedReferences
class TypeChecker:
    @staticmethod
    def is_list(annotation: Type):
        """Returns True if annotation is List[<Any>]"""
        return isinstance(annotation, GenericMeta) and annotation.__origin__ == List

    @staticmethod
    def is_optional(annotation: Type):
        """Returns True if annotation is Optional[<Any>]"""
        return hasattr(annotation, "__origin__") \
               and annotation.__origin__ == Union \
               and len(annotation.__args__) == 2 \
               and isinstance(None, annotation.__args__[1])

    @staticmethod
    def is_type(annotation: Type):
        """Returns True if annotation is Type[<Any>]"""
        return isinstance(annotation, GenericMeta) and annotation.__origin__ == Type
