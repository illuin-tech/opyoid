from typing import Any, TypeVar

InjectedT = TypeVar("InjectedT", bound=Any)
EMPTY = object()


def get_class_full_name(klass):
    try:
        module = klass.__module__
    except AttributeError:
        module = None
    if module == Any.__module__:
        return repr(klass)
    try:
        name = klass.__name__
    except AttributeError:
        name = repr(klass)
    if module is None or module == str.__module__:
        return name
    return module + "." + name
