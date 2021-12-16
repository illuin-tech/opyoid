Conditionals
============

You can add decorators on modules to easily enable or disable them depending on some condition.

### conditional_on_env_var

You can use this condition to enable a module only if an environment variable exists:

```python
import os
from typing import Optional

from opyoid import Module, Injector, SelfBinding, conditional_on_env_var


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: Optional[MyClass] = None):
        self.my_param = my_param


@conditional_on_env_var("ENABLE_SUPER_FEATURE")
class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)


injector = Injector([MyModule()], [SelfBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert my_instance.my_param == None

os.environ["ENABLE_SUPER_FEATURE"] = "true"
injector = Injector([MyModule()], [SelfBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```

You can also use it to enable the module if the variable has the right value:

```python
import os
from typing import Optional

from opyoid import Module, Injector, SelfBinding, conditional_on_env_var

os.environ["ENABLE_SUPER_FEATURE"] = "false"


class MyClass:
    pass


class MyParentClass:
    def __init__(self, my_param: Optional[MyClass] = None):
        self.my_param = my_param


@conditional_on_env_var("ENABLE_SUPER_FEATURE", expected_value="true")
class MyModule(Module):
    def configure(self) -> None:
        self.bind(MyClass)


injector = Injector([MyModule()], [SelfBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert my_instance.my_param == None

os.environ["ENABLE_SUPER_FEATURE"] = "true"
injector = Injector([MyModule()], [SelfBinding(MyParentClass)])
my_instance = injector.inject(MyParentClass)
assert isinstance(my_instance, MyParentClass)
assert isinstance(my_instance.my_param, MyClass)
```
