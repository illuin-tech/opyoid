class InjectException(Exception):
    """Base class for all exceptions."""
    pass


class NonInjectableTypeError(InjectException):
    pass


class NoBindingFound(NonInjectableTypeError):
    pass


class BindingError(InjectException):
    pass
