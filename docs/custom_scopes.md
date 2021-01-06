Custom Scopes
=============

You can inject any custom scope that implements `opyoid.scopes.Scope`, or override an existing one.

Here is an example of a custom scope implementation.

Start by creating a new `Provider`

```python
from opyoid import Provider
from opyoid.utils import InjectedT

EMPTY = object()


class CustomScopedProvider(Provider[InjectedT]):
    def __init__(self, unscoped_provider: Provider[InjectedT]):
        self._unscoped_provider = unscoped_provider
        self._cached_instance = EMPTY
        self._is_scope_activated = False

    def get(self) -> InjectedT:
        if not self._is_scope_activated:
            return self._unscoped_provider.get()

        if self._cached_instance is EMPTY:
            self._cached_instance = self._unscoped_provider.get()

        return self._cached_instance

    def enter(self) -> None:
        self._is_scope_activated = True

    def exit(self) -> None:
        self._is_scope_activated = False
        self._cached_instance = EMPTY
```

Create your own scope:

```python
from types import TracebackType
from typing import List, Optional, Type

from opyoid import Provider
from opyoid.scopes import Scope
from opyoid.utils import InjectedT

from .custom_scoped_provider import CustomScopedProvider


class CustomScope(Scope):
    def __init__(self):
        self._scoped_providers: List[CustomScopedProvider] = []

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        scoped_provider = CustomScopedProvider(inner_provider)
        self._scoped_providers.append(scoped_provider)
        return scoped_provider

    def __enter__(self) -> None:
        for provider in self._scoped_providers:
            provider.enter()

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        for provider in self._scoped_providers:
            provider.exit()
```

To be able to use it you have to bind it:

```python
from opyoid import Injector, SelfBinding

from .custom_scope import CustomScope

class MyType:
    pass


injector = Injector(bindings=[
    SelfBinding(CustomScope),
    SelfBinding(MyType, scope=CustomScope),
])
custom_scope = injector.inject(CustomScope)
instance_1 = injector.inject(MyType)
instance_2 = injector.inject(MyType)

assert instance_1 is not instance_2

with custom_scope:
    instance_3 = injector.inject(MyType)
    instance_4 = injector.inject(MyType)

    assert instance_3 is not instance_1
    assert instance_3 is not instance_2
    assert instance_3 is instance_4

instance_5 = injector.inject(MyType)
instance_6 = injector.inject(MyType)

assert instance_5 is not instance_1
assert instance_5 is not instance_2
assert instance_5 is not instance_3
assert instance_5 is not instance_4
assert instance_5 is not instance_6
```
