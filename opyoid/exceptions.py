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


class NamedError(InjectException):
    """Raised when named_arg is used with an unexpected argument."""
    pass


class CyclicDependencyError(InjectException):
    """Raised when a cyclic dependency is detected."""
    pass
