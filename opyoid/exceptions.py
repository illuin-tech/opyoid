class InjectException(Exception):
    """Base class for all exceptions."""
    pass


class NonInjectableTypeError(InjectException):
    """Raised when a type could not be injected (i.e. they are no corresponding bindings)."""
    pass


class NoBindingFound(NonInjectableTypeError):
    """Raised when no binding was found for a particular class, is caught internally."""
    pass


class BindingError(InjectException):
    """Raised when registering a binding with an invalid value."""
    pass


class AnnotationError(InjectException):
    """Raised when annotated_arg is used with an unexpected argument."""
    pass
