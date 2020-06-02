illuin-inject
=============

Dependency injection library using typings, to easily manage large applications.

This project is inspired from [pinject](https://github.com/google/pinject), [Guice](https://github.com/google/guice),
[HK2](https://javaee.github.io/hk2/) and [Spring](https://spring.io/).

# Usage
### Simple Injection
```python
from illuin_inject import BindingSpec, Injector


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass)
        self.bind(MyParentClass)


injector = Injector([MyBindingSpec()])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```
If they are multiple bindings for the same class, the latest will be used.


### BindingSpec
The binding spec is used to group bindings related to a feature.
You can include a binding spec in another with `install`:
```python
from illuin_inject import BindingSpec, Injector


class MyClass:
    pass


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass)


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyParentBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.install(MyBindingSpec())
        self.bind(MyParentClass)


injector = Injector([MyParentBindingSpec()])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```


### Binding Subclasses
```python
from illuin_inject import BindingSpec, Injector


class MyClass:
    pass


class MySubClass(MyClass):
    pass


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, MySubClass)

injector = Injector([MyBindingSpec()])
my_instance = injector.inject(MyClass)
assert isinstance(my_instance, MySubClass)
```


### Binding Instances
```python
from illuin_inject import BindingSpec, Injector


class MyClass:
    def __init__(self, my_param: str):
        self.my_param = my_param

my_instance = MyClass("hello")


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, to_instance=my_instance)


injector = Injector([MyBindingSpec()])
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
from illuin_inject import BindingSpec, Injector, SingletonScope


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, scope=SingletonScope)
        self.bind(MyParentClass, scope=SingletonScope)

injector = Injector([MyBindingSpec()])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)
parent_instance = injector.inject(MyParentClass)
assert instance_1 is instance_2
assert instance_1 is parent_instance.my_param
```


#### PerLookup Scope
If you use the per lookup scope, a new instance will be created every time each class is injected.
```python
from illuin_inject import BindingSpec, Injector, PerLookupScope


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, scope=PerLookupScope)
        self.bind(MyParentClass)

injector = Injector([MyBindingSpec()])
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

from illuin_inject import BindingSpec, Injector, ThreadScope


class MyClass:
    pass


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, scope=ThreadScope)

injector = Injector([MyBindingSpec()])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)

def thread_target():
    instance_3 = injector.inject(MyClass)
    assert instance_1 is not instance_3

Thread(target=thread_target).start()

assert instance_1 is instance_2
```

#### Custom Scope
You can inject any custom scope that implements `illuin_inject.scopes.Scope`, or override an existing one:

```python
from illuin_inject import BindingSpec, Injector, Provider
from illuin_inject.scopes import Scope
from illuin_inject.typings import InjectedT


class MyScope(Scope):
    @classmethod
    def get_scoped_provider(cls, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return inner_provider


class MyClass:
    pass


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, scope=MyScope)

injector = Injector([MyBindingSpec()])
instance_1 = injector.inject(MyClass)
instance_2 = injector.inject(MyClass)
assert instance_1 is not instance_2
```

### Annotations
You can use annotations to inject different objects for the same type.

```python
from illuin_inject import annotated_arg, BindingSpec, Injector


class MyClass1:
    @annotated_arg("my_param", "class_1_param")
    def __init__(self, my_param: str):
        self.my_param = my_param

class MyClass2:
    @annotated_arg("my_param", "class_2_param")
    def __init__(self, my_param: str):
        self.my_param = my_param


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass1)
        self.bind(MyClass2)
        self.bind(str, to_instance="my_value_1", annotation="class_1_param")
        self.bind(str, to_instance="my_value_2", annotation="class_2_param")

injector = Injector([MyBindingSpec()])
instance_1 = injector.inject(MyClass1)
assert isinstance(instance_1, MyClass1)
assert instance_1.my_param == "my_value_1"
instance_2 = injector.inject(MyClass2)
assert isinstance(instance_2, MyClass2)
assert instance_2.my_param == "my_value_2"
```


### Bindings without BindingSpec
If you prefer, you can add bindings to your injector without creating a BindingSpec class (or using both).

```python
from illuin_inject import BindingSpec, ClassBinding, Injector


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: MyClass):
        self.my_param = my_param


class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass)


injector = Injector([MyBindingSpec()], [ClassBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```

The same options of BindingSpec.bind are available when using bindings:
```python
from illuin_inject import ClassBinding, InstanceBinding, PerLookupScope


class MyClass:
    pass


class MySubClass(MyClass):
    pass

my_instance = MyClass()

ClassBinding(MyClass)  # binding a class to itself
ClassBinding(MyClass, MySubClass)  # binding a class to a subclass
ClassBinding(MyClass, scope=PerLookupScope)  # specifying scope
InstanceBinding(MyClass, my_instance)  # binding an instance
ClassBinding(MyClass, annotation="my_annotation")  # binding a class to itself with an annotation
InstanceBinding(MyClass, my_instance, annotation="my_annotation")  # binding an instance with an annotation
```


### Injecting lists
If no explicit binding is defined, all the bindings to the item type will be used in the order of the binding. 


```python
from typing import List

from illuin_inject import BindingSpec, Injector

class MyClass:
    pass

class SubClass(MyClass):
    pass

class MyParentClass:
    def __init__(self, my_param: List[MyClass]):
        self.my_param = my_param

my_instance = MyClass()

class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass, SubClass)
        self.bind(MyClass)
        self.bind(MyClass, to_instance=my_instance)
        self.bind(MyParentClass)


injector = Injector([MyBindingSpec()])
parent_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, list)
assert len(my_instance.my_param) == 3
assert isinstance(my_instance.my_param[0], SubClass)
assert isinstance(my_instance.my_param[1], MyClass)
assert my_instance.my_param[2] is my_instance
```


### Injecting Type
If no explicit binding is defined, the last class binding will be used to inject a type:

```python
from typing import Type

from illuin_inject import BindingSpec, Injector

class MyClass:
    pass

class SubClass(MyClass):
    pass

class MyParentClass:
    def __init__(self, my_param: Type[MyClass]):
        self.my_param = my_param

my_instance = MyClass()

class MyBindingSpec(BindingSpec):
    def configure(self) -> None:
        self.bind(MyClass)
        self.bind(MyClass, SubClass)
        self.bind(MyClass, to_instance=my_instance)
        self.bind(MyParentClass)


injector = Injector([MyBindingSpec()])
parent_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert my_instance.my_param is SubClass
```


## Dataclasses
`illuin_inject` can inject classes and parameters defined with the `attrs` library and python data classes.


# Limitations
- The only supported generic types are `List`, `Set`, `Tuple`, `Optional` and `Type` (and any combination of them).
Other generics must be bound explicitly (e.g. you must bind a tuple to `Tuple[MyClass]` if you want to inject it).
- Be careful when using generics, the bindings will only be used if the type matches exactly. For example, you cannot
implicitly bind `MyClass[T]` to inject `MyClass`, or `MyClass[str]` to inject `MyClass[T]`. You need to bind something
to `MyClass[str]` to be able to inject it.
