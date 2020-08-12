Annotations
===========

You can use annotations to inject different objects for the same type.

```python
from opyoid import annotated_arg, Module, Injector


class MyClass1:
    @annotated_arg("my_param", "class_1_param")
    def __init__(self, my_param: str):
        self.my_param = my_param

class MyClass2:
    @annotated_arg("my_param", "class_2_param")
    def __init__(self, my_param: str):
        self.my_param = my_param


class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass1)
        self.bind(MyClass2)
        self.bind(str, to_instance="my_value_1", annotation="class_1_param")
        self.bind(str, to_instance="my_value_2", annotation="class_2_param")

injector = Injector([MyModule()])
instance_1 = injector.inject(MyClass1)
assert isinstance(instance_1, MyClass1)
assert instance_1.my_param == "my_value_1"
instance_2 = injector.inject(MyClass2)
assert isinstance(instance_2, MyClass2)
assert instance_2.my_param == "my_value_2"
```
