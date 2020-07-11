MultiBindings
=============

### Injecting lists
Use MultiBindings to inject lists, sets and tuples.
Items can be bound to classes, instances and factories.


```python
from typing import List

from illuin_inject import Module, Injector, Factory

class MyClass:
    pass

class SubClass(MyClass):
    pass

class MyFactory(Factory[MyClass]):
    def create(self) -> MyClass:
        return MyClass()

my_instance = MyClass()
my_factory = MyFactory()


class MyModule(Module):
    def configure(self) -> None:
        self.multi_bind(
            MyClass,
            [
                self.bind_item(to_class=SubClass),
                self.bind_item(to_class=MyClass),
                self.bind_item(to_instance=my_instance),
                self.bind_item(to_factory=my_factory),
                self.bind_item(to_factory=MyFactory),
            ]
        )


injector = Injector([MyModule()])
parent_instance = injector.inject(List[MyClass])
assert isinstance(my_instance, list)
assert len(my_instance) == 5
assert isinstance(my_instance[0], SubClass)
assert isinstance(my_instance[1], MyClass)
assert my_instance[2] is my_instance
assert isinstance(my_instance[3], SubClass)
assert isinstance(my_instance[4], MyClass)
```

### Manually creating bindings

You can create MultiBindings and ItemBindings manually:

```python
from illuin_inject import Injector, Factory, ItemBinding, MultiBinding

class MyClass:
    pass

class SubClass(MyClass):
    pass

class MyFactory(Factory[MyClass]):
    def create(self) -> MyClass:
        return MyClass()

my_instance = MyClass()
my_factory = MyFactory()

injector = Injector(bindings=[
    MultiBinding(MyClass, [
        ItemBinding(bound_type=SubClass),
        ItemBinding(bound_instance=my_instance),
        ItemBinding(bound_factory=my_factory),
    ])
])
```


### Scoped Bindings

You can specify a scope to a multi binding (default is `SingletonScope`).

The scope will apply to the list object and all its items.
If you are injecting sets or tuples with a SingletonScope, the item instances will be shared between them.

```python
from typing import Tuple
from illuin_inject import Injector, ImmediateScope, ItemBinding, MultiBinding

class MyClass:
    pass


injector = Injector(bindings=[
    MultiBinding(MyClass, [
        ItemBinding(bound_type=MyClass),
    ], scope=ImmediateScope)
])

tuple_1 = injector.inject(Tuple[MyClass])
tuple_2 = injector.inject(Tuple[MyClass])
assert tuple_1[0] is not tuple_2[0]
```

### Extending a MultiBinding

You can use the argument `override_bindings` (defaults to `True`) in the `MultiBinding` constructor and
`Module.multi_bind` to specify if the item bindings should override or extend the preexisting bindings.

```python
from typing import List
from illuin_inject import Module, Injector

class MyClass:
    pass

class Module1(Module):
    def configure(self) -> None:
        self.multi_bind(MyClass, [self.bind_item(to_class=MyClass)])

class Module2(Module):
    def configure(self) -> None:
        self.install(Module1())
        self.multi_bind(MyClass, [self.bind_item(to_instance=MyClass())], override_bindings=False)



injector = Injector([Module2()])

injected_list = injector.inject(List[MyClass])
assert len(injected_list) == 2
```
