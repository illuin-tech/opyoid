Opyoid
======

![CI](https://github.com/illuin-tech/opyoid/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/illuin-tech/opyoid/branch/master/graph/badge.svg)](https://codecov.io/gh/illuin-tech/opyoid)

Dependency injection library using typings, to easily manage large applications.

This project is inspired from [Guice](https://github.com/google/guice).

# Installation

Run `pip install opyoid` to install from PyPI.

Run `pip install .` to install from sources.

This project follows the [Semantic Versioning Specification](https://semver.org/).
All breaking changes are described in the [Changelog](CHANGELOG.md).


# Usage
### Simple Injection
```python
from opyoid import Module, Injector


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)
        self.bind(MyParentClass)


injector = Injector([MyModule])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```
If they are multiple bindings for the same class, the latest will be used.


### Module
The module is used to group bindings related to a feature.
You can include a module in another with `install`:
```python
from opyoid import Module, Injector


class MyClass:
    pass


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyParentModule(Module):
    def configure(self) -> None:
        self.install(MyModule)
        self.bind(MyParentClass)


injector = Injector([MyParentModule])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```


### Binding Subclasses
```python
from opyoid import Module, Injector


class MyClass:
    pass


class MySubClass(MyClass):
    pass


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass, to_class=MySubClass)

injector = Injector([MyModule])
my_instance = injector.inject(MyClass)
assert isinstance(my_instance, MySubClass)
```


### Binding Instances
```python
from opyoid import Module, Injector


class MyClass:
    def __init__(self, my_param: str):
        self.my_param = my_param

my_instance = MyClass("hello")


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass, to_instance=my_instance)


injector = Injector([MyModule])
injected_instance = injector.inject(MyClass)
assert my_instance is injected_instance
```


### Binding scopes
When binding a class, you can choose the scope in which it will be instantiated.
This will only have an effect when binding classes, not instances.


#### Singleton Scope
By default, all classes are instantiated in a Singleton scope.
This means that only one instance of each class will be created, and it will be shared between all classes requiring it.

```python
from opyoid import Module, Injector, SingletonScope


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass, scope=SingletonScope)
        self.bind(MyParentClass, scope=SingletonScope)

injector = Injector([MyModule])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)
parent_instance = injector.inject(MyParentClass)
assert instance_1 is instance_2
assert instance_1 is parent_instance.my_param
```


#### PerLookup Scope
If you use the per lookup scope, a new instance will be created every time each class is injected.
```python
from opyoid import Module, Injector, PerLookupScope


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass, scope=PerLookupScope)
        self.bind(MyParentClass)

injector = Injector([MyModule])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)
parent_instance = injector.inject(MyParentClass)
assert instance_1 is not instance_2
assert instance_1 is not parent_instance.my_param
```


#### Thread Scope
This scope only creates a new instance the first time that the class is injected in the current thread.
There will only be one instance of each class in each thread, and two instances injected from different threads will be
different objects.

```python
from threading import Thread

from opyoid import Module, Injector, ThreadScope


class MyClass:
    pass


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass, scope=ThreadScope)

injector = Injector([MyModule])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)

def thread_target():
    instance_3 = injector.inject(MyClass)
    assert instance_1 is not instance_3

Thread(target=thread_target).start()

assert instance_1 is instance_2
```


### Bindings without Module
If you prefer, you can add bindings to your injector without creating a Module class (or using both).

```python
from opyoid import Module, Injector, SelfBinding


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)


injector = Injector([MyModule], [SelfBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```

The same options of Module.bind are available when using bindings:
```python
from opyoid import ClassBinding, InstanceBinding, PerLookupScope, SelfBinding


class MyClass:
    pass


class MySubClass(MyClass):
    pass

my_instance = MyClass()

SelfBinding(MyClass)  # binding a class to itself
ClassBinding(MyClass, MySubClass)  # binding a class to a subclass
SelfBinding(MyClass, scope=PerLookupScope)  # specifying scope
InstanceBinding(MyClass, my_instance)  # binding an instance
SelfBinding(MyClass, named="my_name")  # binding a class to itself with a specific name
InstanceBinding(MyClass, my_instance, named="my_name")  # binding an instance with a specific name
```

### Injecting Type
If no explicit binding is defined, the last class binding will be used to inject a type:

```python
from typing import Type

from opyoid import Module, Injector

class MyClass:
    pass

class SubClass(MyClass):
    pass

class MyParentClass:
    def __init__(self, my_param: Type[MyClass]):
        self.my_param = my_param

my_instance = MyClass()

class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)
        self.bind(MyClass, to_instance=my_instance)
        self.bind(MyClass, to_class=SubClass)
        self.bind(MyParentClass)


injector = Injector([MyModule])
parent_instance = injector.inject(MyParentClass)
assert isinstance(parent_instance, MyParentClass)
assert parent_instance.my_param is SubClass
```


## Dataclasses
`opyoid` can inject classes and parameters defined with the `attrs` library and python data classes.


##  Notes about Generics
- The supported generic types are `List`, `Set`, `Tuple`, `Optional`, `Union` and `Type` (and any combination of them).
Other generics must be bound explicitly (e.g. you must bind a dict to `Dict[str, MyClass]` if you want to inject it).
- Be careful when using generics, the bindings will only be used if the type matches exactly. For example, you cannot
implicitly bind `MyClass[T]` to inject `MyClass`, or `MyClass[str]` to inject `MyClass[T]`. You need to bind something
to `MyClass[str]` to be able to inject it.

# Advanced usage
More advanced features and examples are available in the [./docs](docs) folder.
