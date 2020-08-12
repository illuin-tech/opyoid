from inspect import Parameter, Signature, signature
from typing import Callable, Generic, Mapping, Type, TypeVar, cast

from opyoid.exceptions import AnnotationError

WrappedT = TypeVar("WrappedT")


class Annotated(Generic[WrappedT]):
    annotation: str = None
    original_type: Type[WrappedT]

    @classmethod
    def get_annotated_class(cls, original_type: str, annotation: str) -> Type["Annotated"]:
        return cast(
            Type[Annotated],
            type(
                cls.__name__,
                (cls,), {
                    "annotation": annotation,
                    "original_type": original_type,
                },
            ),
        )


def annotated_arg(arg_name: str, annotation: str) -> Callable[[Callable], Callable]:
    """Decorator used to annotate constructor arguments.

    Use it to specify multiple bindings for the same type.
    """

    def wrapped_init(init: Callable) -> Callable:
        init_signature = signature(init)
        parameters: Mapping[str, Parameter] = init_signature.parameters
        if arg_name not in parameters:
            raise AnnotationError(f"Cannot add annotation on unknown parameter '{arg_name}'")
        parameter = parameters[arg_name]
        if parameter.annotation is Parameter.empty:
            raise AnnotationError(f"Cannot add annotation on untyped parameter '{arg_name}'")
        new_parameter = parameter.replace(annotation=Annotated.get_annotated_class(parameter.annotation, annotation))
        init.__signature__ = Signature([
            new_parameter if parameter.name == arg_name else parameter
            for parameter in parameters.values()
        ])
        return init

    return wrapped_init
