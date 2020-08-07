from typing import Optional, Type, Union

import attr

from illuin_inject.provider import Provider
from illuin_inject.bindings.binding import Binding
from illuin_inject.exceptions import BindingError
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class ProviderBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_provider: Union[Type[Provider[InjectedT]], Provider[InjectedT]]
    scope: Type[Scope] = SingletonScope
    _annotation: Optional[str] = None

    def __attrs_post_init__(self) -> None:
        if isinstance(self.bound_provider, Provider) and self.scope is not SingletonScope:
            raise BindingError(f"Invalid binding: cannot set a scope to a provider instance, got {self.scope!r}")
        if not isinstance(self.bound_provider, Provider) \
            and not (isinstance(self.bound_provider, type) and issubclass(self.bound_provider, Provider)):
            raise BindingError(f"Invalid {self!r}: bound provider must be a Provider instance or subclass,"
                               f" got {self.bound_provider!r}")

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def annotation(self) -> Optional[str]:
        return self._annotation
