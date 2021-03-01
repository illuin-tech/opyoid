from typing import Any, Type, TypeVar, Union, cast

from .named import Named

InjectedT = TypeVar("InjectedT", bound=Any)
EMPTY = object()


def get_class_full_name(klass: Union[Type, str]) -> str:
    if isinstance(klass, str):
        return klass
    if isinstance(klass, type) and issubclass(klass, Named):
        return get_class_full_name(cast(Type[Named], klass).original_type)
    if hasattr(klass, "__origin__"):
        return repr(klass)
    try:
        module = klass.__module__
    except AttributeError:
        module = None
    try:
        name = klass.__name__
    except AttributeError:
        name = repr(klass)
    if module is None or module == str.__module__:
        return name
    return module + "." + name
