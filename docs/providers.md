Providers
=========

All bindings are transformed by the library into providers so that they can be injected.
You can create your own providers or inject them to control how the classes are instantiated.


## ProviderBinding
Sometimes you need to inject a class from an external library or some legacy code that you do not control.
If these classes are not typed, you can use a Provider to be able to inject them:

```python
from opyoid import Module, Injector


class MyUntypedClass:
    def __init__(self, my_param):  # No typings :(
        self.my_param = my_param


class MyModule(Module):
    @staticmethod
    def provide_untyped_class(my_param: str) -> MyUntypedClass:  # This can be a method, or any function
        return MyUntypedClass(my_param)

    def configure(self) -> None:
        self.bind(str, to_instance="my_string")
        # You can bind
        self.bind(MyUntypedClass, to_provider=self.provide_untyped_class)
        # You can use a scope and specify an argument name
        # self.bind(MyUntypedClass, to_provider=self.provide_untyped_class, scope=SingletonScope, named="my_name")


injector = Injector([MyModule])
injected_instance = injector.inject(MyUntypedClass)
assert isinstance(injected_instance, MyUntypedClass)
assert injected_instance.my_param == "my_string"
```

```python
from opyoid import Injector, InstanceBinding, Provider, ProviderBinding


class MyUntypedClass:
    def __init__(self, my_param):  # No typings :(
        self.my_param = my_param

def provide_untyped_class(my_param: str):  # This function must be typed
        return MyUntypedClass(my_param)


injector = Injector(bindings=[
    InstanceBinding(str, "my_string"),
    ProviderBinding(MyUntypedClass, provide_untyped_class),
    # You can also use a scope and an argument name
    # ProviderBinding(MyUntypedClass, provide_untyped_class, scope=SingletonScope, named="my_name"),
])
injected_instance = injector.inject(MyUntypedClass)
assert isinstance(injected_instance, MyUntypedClass)
assert injected_instance.my_param == "my_string"
```

Note that if you bind a `ProviderBinding` to your class, the bound provider class or instance will be injected when you
require `Provider[MyClass]`.
