Providers
=========

All bindings are transformed by the library into providers so that they can be injected.
You can create your own providers or inject them to control how the classes are instantiated.


## ProviderBinding
Sometimes you need to inject a class from an external library or some legacy code that you do not control.
If these classes are not typed, you can use a Provider to be able to inject them:

```python
from opyoid import Module, Injector, Provider


class MyUntypedClass:
    def __init__(self, my_param):  # No typings :(
        self.my_param = my_param

class MyUntypedClassProvider(Provider[MyUntypedClass]):
    def __init__(self, my_param: str):  # This constructor must be typed
        self.my_param = my_param

    def get(self) -> MyUntypedClass:
        return MyUntypedClass(self.my_param)


class MyModule(Module):
    def configure(self) -> None:
        self.bind(str, to_instance="my_string")
        self.bind(MyUntypedClass, to_provider=MyUntypedClassProvider)
        # You can also bind to a provider instance
        # self.bind(MyUntypedClass, to_provider=MyUntypedClassProvider())
        # You can use a scope and an annotation
        # self.bind(MyUntypedClass, to_provider=MyUntypedClassProvider, scope=SingletonScope, annotation="my_annotation")


injector = Injector([MyModule()])
injected_instance = injector.inject(MyUntypedClass)
assert isinstance(injected_instance, MyUntypedClass)
assert injected_instance.my_param == "my_string"
```

```python
from opyoid import Injector, InstanceBinding, Provider, ProviderBinding


class MyUntypedClass:
    def __init__(self, my_param):  # No typings :(
        self.my_param = my_param

class MyUntypedClassProvider(Provider[MyUntypedClass]):
    def __init__(self, my_param: str):  # This constructor must be typed
        self.my_param = my_param

    def get(self) -> MyUntypedClass:
        return MyUntypedClass(self.my_param)


injector = Injector(bindings=[
    InstanceBinding(str, "my_string"),
    ProviderBinding(MyUntypedClass, MyUntypedClassProvider),
    # You can also bind to a provider instance, use a scope and an annotation
    # ProviderBinding(MyUntypedClass, MyUntypedClassProvider(), scope=SingletonScope, annotation="my_annotation"),
])
injected_instance = injector.inject(MyUntypedClass)
assert isinstance(injected_instance, MyUntypedClass)
assert injected_instance.my_param == "my_string"
```

## Provider injection

Providers can also be injected. This is useful if you want to delay the instance creation until you really need it.

```python
from opyoid import Module, Injector, Provider

class MyClass:
    created_instances = 0

    def __init__(self):
        MyClass.created_instances += 1


class MyParentClass:
    def __init__(self, my_param: Provider[MyClass]):
        self.my_param = my_param

class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)
        self.bind(MyParentClass)

injector = Injector([MyModule()])
injected_parent = injector.inject(MyParentClass)
assert isinstance(injected_parent, MyParentClass)
assert isinstance(injected_parent.my_param, Provider)
assert MyClass.created_instances == 0
instance = injected_parent.my_param.get()
assert isinstance(instance, MyClass)
assert MyClass.created_instances == 1
```

Note that if you bound a `ProviderBinding` to your class, the bound provider class or instance will be injected when you
require `Provider[MyClass]`.
