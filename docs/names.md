Names
=====

If you specify a name in your binding, only parameters with the same name will use this binding.
If no bindings with the same name are found, a binding without a name will be used as a fallback if available.
You can use this to inject different objects for the same type.

```python
from opyoid import Module, Injector


class MyClass1:
    def __init__(self, class_1_param: str, other_param: str):
        self.class_1_param = class_1_param
        self.other_param = other_param

class MyClass2:
    def __init__(self, class_2_param: str):
        self.class_2_param = class_2_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass1)
        self.bind(MyClass2)
        self.bind(str, to_instance="my_value_1", named="class_1_param")
        self.bind(str, to_instance="my_value_2", named="class_2_param")
        self.bind(str, to_instance="default_value")

injector = Injector([MyModule()])
instance_1 = injector.inject(MyClass1)
assert isinstance(instance_1, MyClass1)
assert instance_1.class_1_param == "my_value_1"
assert instance_1.other_param == "default_value"
instance_2 = injector.inject(MyClass2)
assert isinstance(instance_2, MyClass2)
assert instance_2.class_2_param == "my_value_2"
```

If you want to specify a different name, for example if multiple classes use the same type with the same name,
you can use the `@named_arg` decorator.
This will not change the signature of the constructor, only opyoid will detect the new name.
Using this decorator will also prevent the unnamed binding to be used.

```python
from opyoid import named_arg, Module, Injector


class MyClass1:
    @named_arg("my_param", "class_1_param")
    @named_arg("other_param", "class_1_other_param")
    def __init__(self, my_param: str, other_param: str = "fallback_value"):
        self.my_param = my_param
        self.other_param = other_param

class MyClass2:
    @named_arg("my_param", "class_2_param")
    def __init__(self, my_param: str):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass1)
        self.bind(MyClass2)
        self.bind(str, to_instance="my_value_1", named="class_1_param")
        self.bind(str, to_instance="my_value_2", named="class_2_param")
        self.bind(str, to_instance="default_value")

injector = Injector([MyModule()])
instance_1 = injector.inject(MyClass1)
assert isinstance(instance_1, MyClass1)
assert instance_1.my_param == "my_value_1"
assert instance_1.other_param == "fallback_value"
instance_2 = injector.inject(MyClass2)
assert isinstance(instance_2, MyClass2)
assert instance_2.my_param == "my_value_2"
```
