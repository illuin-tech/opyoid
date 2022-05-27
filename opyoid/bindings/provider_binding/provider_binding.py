from typing import Callable, Optional, Type, Union

import attr

from opyoid.bindings.binding import Binding
from opyoid.exceptions import BindingError
from opyoid.provider import Provider
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT, get_class_full_name, get_function_full_name


@attr.s(auto_attribs=True, frozen=True, repr=False)
class ProviderBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_provider: Union[Type[Provider[InjectedT]], Provider[InjectedT], Callable[..., InjectedT]]
    scope: Type[Scope] = attr.ib(default=SingletonScope, kw_only=True)
    _named: Optional[str] = attr.ib(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if isinstance(self.bound_provider, Provider) and self.scope is not SingletonScope:
            raise BindingError(f"Invalid binding: cannot set a scope to a provider instance, got {self.scope!r}")
        if not isinstance(self.bound_provider, Provider) and not callable(self.bound_provider):
            raise BindingError(
                f"Invalid {self!r}: bound provider must be a Provider instance or subclass, or a method,"
                f" got {self.bound_provider!r}"
            )

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        if isinstance(self.bound_provider, Provider):
            provider_string = repr(self.bound_provider)
        elif isinstance(self.bound_provider, type):
            provider_string = get_class_full_name(self.bound_provider)
        else:
            provider_string = get_function_full_name(self.bound_provider)
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r} -> {provider_string}{scope_string})"
