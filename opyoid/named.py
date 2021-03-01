from inspect import Parameter, Signature, signature
from typing import Callable, Generic, Mapping, Type, TypeVar, Union, cast

from opyoid.exceptions import NamedError

WrappedT = TypeVar("WrappedT")


class Named(Generic[WrappedT]):
    name: str = None
    original_type: Type[WrappedT]

    @classmethod
    def get_named_class(cls, original_type: Union[Type[WrappedT], str], name: str) -> Type["Named"]:
        return cast(
            Type[Named],
            type(
                cls.__name__,
                (cls,), {
                    "name": name,
                    "original_type": original_type,
                },
            ),
        )


def named_arg(arg_name: str, name: str) -> Callable[[Callable], Callable]:
    """Decorator used to name constructor arguments.

    Use it to specify multiple bindings for the same type.
    """

    def wrapped_init(init: Callable) -> Callable:
        init_signature = signature(init)
        parameters: Mapping[str, Parameter] = init_signature.parameters
        if arg_name not in parameters:
            raise NamedError(f"Cannot add name on unknown parameter '{arg_name}'")
        parameter = parameters[arg_name]
        if parameter.annotation is Parameter.empty:
            raise NamedError(f"Cannot add name on untyped parameter '{arg_name}'")
        new_parameter = parameter.replace(annotation=Named.get_named_class(parameter.annotation, name))
        init.__signature__ = Signature([
            new_parameter if parameter.name == arg_name else parameter
            for parameter in parameters.values()
        ])
        return init

    return wrapped_init
