from typing import Optional, Type, Union

import attr

from illuin_inject.bindings.binding import Binding
from illuin_inject.exceptions import BindingError
from illuin_inject.factory import Factory
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class FactoryBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_factory: Union[Type[Factory[InjectedT]], Factory[InjectedT]]
    scope: Type[Scope] = SingletonScope
    _annotation: Optional[str] = None

    def __attrs_post_init__(self) -> None:
        if isinstance(self.bound_factory, Factory) and self.scope is not SingletonScope:
            raise BindingError(f"Invalid binding: cannot set a scope to a factory instance, got {self.scope!r}")
        if not isinstance(self.bound_factory, Factory) \
            and not (isinstance(self.bound_factory, type) and issubclass(self.bound_factory, Factory)):
            raise BindingError(
                f"Invalid {self!r}: bound factory must be a Factory instance or subclass, got {self.bound_factory!r}")

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def annotation(self) -> Optional[str]:
        return self._annotation
